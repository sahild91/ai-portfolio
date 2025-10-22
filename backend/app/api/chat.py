from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

from app.services.chat_service import get_chat_service
from app.models.chat import ChatMessageCreate, ChatResponse
from app.middleware.cost_limiter import get_cost_limiter  # ADDED
from app.utils.db import db_manager  # CHANGED: Use existing db_manager
from app.utils.logger import logger


router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    portfolio_id: str = Field(..., description="Portfolio ID")
    session_id: str = Field(..., description="Session ID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Tell me about your React projects",
                "portfolio_id": "507f1f77bcf86cd799439011",
                "session_id": "sess_abc123xyz"
            }
        }
    }


class ChatResponseModel(BaseModel):
    """Response schema for chat endpoint"""
    success: bool
    response: str
    actions: List[Dict[str, Any]] = []
    context_sources: List[Dict[str, Any]] = []
    metadata: Dict[str, Any]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "response": "I've worked on several React projects...",
                "actions": [],
                "context_sources": [
                    {
                        "content_id": "123",
                        "title": "React Dashboard",
                        "type": "project",
                        "url": "/projects/react-dashboard",
                        "score": 0.92
                    }
                ],
                "metadata": {
                    "tokens_used": 150,
                    "cost": 0.0003,
                    "response_time": 1.2,
                    "context_count": 3,
                    "from_cache": False
                }
            }
        }
    }


class SuggestedQuestionsResponse(BaseModel):
    """Response schema for suggested questions"""
    questions: List[str]


@router.post("/", response_model=ChatResponseModel)
async def chat(request: ChatRequest):  # CHANGED: Removed db_client from params
    """
    Process a chat message
    
    This endpoint:
    1. Checks cost limits (session, daily, monthly)
    2. Searches for relevant context using vector search
    3. Generates AI response using OpenAI
    4. Returns response with actions and metadata
    5. Tracks costs and performance
    
    Args:
        request: ChatRequest with query, portfolio_id, session_id
        
    Returns:
        ChatResponseModel with AI response and metadata
        
    Raises:
        HTTPException: If processing fails or rate limited
    """
    try:
        logger.info(f"Chat request from session {request.session_id}: '{request.query[:50]}'")
        
        # Get services
        limiter = get_cost_limiter()
        chat_service = get_chat_service()
        
        # CHANGED: Get MongoDB client from db_manager
        db_client = db_manager.client
        
        # Check cost limits (Tier 1, 2, 3)
        check_result = await limiter.check_limits(
            session_id=request.session_id,
            portfolio_id=request.portfolio_id,
            db_client=db_client
        )
        
        if not check_result["allowed"]:
            logger.warning(
                f"Rate limit hit for session {request.session_id} "
                f"(tier: {check_result['tier']})"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=check_result["error"]
            )
        
        # Process message
        result = chat_service.process_message(
            query=request.query,
            portfolio_id=request.portfolio_id,
            session_id=request.session_id,
            conversation_history=None  # TODO: Load from database
        )
        
        # Record request for session tracking
        limiter.record_request(
            session_id=request.session_id,
            cost=result["metadata"]["cost"]
        )
        
        # Track usage in MongoDB for daily/monthly limits
        await limiter.track_usage(
            portfolio_id=request.portfolio_id,
            cost=result["metadata"]["cost"],
            tokens=result["metadata"]["tokens_used"],
            db_client=db_client
        )
        
        logger.info(
            f"Chat response generated - "
            f"tokens: {result['metadata']['tokens_used']}, "
            f"cost: ${result['metadata']['cost']:.6f}, "
            f"cached: {result['metadata']['from_cache']}"
        )
        
        # Return response
        return ChatResponseModel(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limits)
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/suggestions/{portfolio_id}", response_model=SuggestedQuestionsResponse)
async def get_suggestions(portfolio_id: str):
    """
    Get suggested questions for a portfolio
    
    Args:
        portfolio_id: Portfolio ID
        
    Returns:
        List of suggested questions
    """
    try:
        chat_service = get_chat_service()
        questions = chat_service.get_suggested_questions(portfolio_id)
        
        return SuggestedQuestionsResponse(questions=questions)
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve suggestions"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for chat service
    
    Returns:
        Status of chat service dependencies
    """
    try:
        chat_service = get_chat_service()
        
        # Check vector search
        vector_health = chat_service.vector_service.health_check()
        
        return {
            "status": "healthy",
            "vector_search": vector_health.status,
            "openai": "connected" if vector_health.openai_connected else "disconnected",
            "timestamp": vector_health.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }