from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum

# Import base classes
try:
    from app.models import BaseDBModel, PyObjectId
except ImportError:
    from . import BaseDBModel, PyObjectId


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enum"""
    TEXT = "text"
    ACTION = "action"
    ERROR = "error"


class ChatMessage(BaseModel):
    """
    Individual chat message
    Embedded within ChatConversation
    """
    
    role: MessageRole = Field(..., description="Message sender role")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # AI Response Metadata (for assistant messages)
    tokens_used: Optional[int] = Field(None, description="Tokens used for this message")
    cost: Optional[float] = Field(None, description="API cost for this message")
    model: Optional[str] = Field(None, description="AI model used")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    
    # Context Information
    context_used: Optional[List[str]] = Field(None, description="Content IDs used for context")
    vector_search_results: Optional[int] = Field(None, description="Number of vector results found")
    
    # Actions (for dynamic UI updates)
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="UI actions triggered")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "user",
                "content": "Tell me about your React projects",
                "message_type": "text",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }


class ConversationStatus(str, Enum):
    """Conversation status enum"""
    ACTIVE = "active"
    ENDED = "ended"
    ARCHIVED = "archived"


class ChatConversation(BaseDBModel):
    """
    Chat conversation with message history
    Multi-tenant: Each conversation belongs to one portfolio
    """
    
    # Multi-tenant key
    portfolio_id: PyObjectId = Field(..., description="Portfolio this conversation belongs to")
    
    # Session Identification
    session_id: str = Field(..., description="Unique session identifier")
    
    # Messages
    messages: List[ChatMessage] = Field(default_factory=list, description="Conversation messages")
    
    # Conversation Metadata
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE, description="Conversation status")
    user_ip: Optional[str] = Field(None, description="User IP address (anonymized)")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    # Analytics
    total_messages: int = Field(default=0, description="Total message count")
    user_messages: int = Field(default=0, description="User message count")
    assistant_messages: int = Field(default=0, description="Assistant message count")
    
    # Cost Tracking
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost: float = Field(default=0.0, description="Total API cost")
    
    # Engagement Metrics
    first_message_at: Optional[datetime] = Field(None, description="First message timestamp")
    last_message_at: Optional[datetime] = Field(None, description="Last message timestamp")
    duration_seconds: Optional[int] = Field(None, description="Conversation duration in seconds")
    
    # Data Retention (TTL)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=30),
        description="Conversation expiry date (30 days default)"
    )
    
    # Feedback
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    feedback_text: Optional[str] = Field(None, description="User feedback")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "portfolio_id": "507f1f77bcf86cd799439011",
                "session_id": "sess_abc123xyz",
                "messages": [
                    {
                        "role": "user",
                        "content": "Show me your React projects",
                        "message_type": "text"
                    },
                    {
                        "role": "assistant",
                        "content": "I found 3 React projects...",
                        "message_type": "text",
                        "tokens_used": 150,
                        "cost": 0.0003
                    }
                ],
                "total_messages": 2,
                "status": "active"
            }
        }
    }


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    session_id: str
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    portfolio_id: PyObjectId


class ChatConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    portfolio_id: PyObjectId
    session_id: str
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None


class ChatConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    status: Optional[ConversationStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for chat API"""
    success: bool
    message: str
    session_id: str
    
    # AI Response
    response_text: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    response_time: Optional[float] = None
    
    # Context
    context_sources: Optional[List[str]] = None
    vector_results_count: Optional[int] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Response generated successfully",
                "session_id": "sess_abc123xyz",
                "response_text": "I found 3 React projects in my portfolio...",
                "actions": [
                    {
                        "type": "filter_projects",
                        "params": {"tech": "React"}
                    }
                ],
                "tokens_used": 150,
                "cost": 0.0003,
                "response_time": 1.2
            }
        }
    }


class ConversationListResponse(BaseModel):
    """Paginated conversation list response"""
    conversations: List[ChatConversation]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConversationFilter(BaseModel):
    """Schema for filtering conversations"""
    portfolio_id: PyObjectId
    session_id: Optional[str] = None
    status: Optional[ConversationStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_messages: Optional[int] = None
    has_rating: Optional[bool] = None


class ConversationStats(BaseModel):
    """Conversation statistics for analytics"""
    portfolio_id: PyObjectId
    total_conversations: int
    active_conversations: int
    total_messages: int
    avg_messages_per_conversation: float
    total_tokens: int
    total_cost: float
    avg_response_time: float
    avg_rating: Optional[float] = None
    period_start: datetime
    period_end: datetime


__all__ = [
    "ChatMessage",
    "ChatConversation",
    "ChatMessageCreate",
    "ChatConversationCreate",
    "ChatConversationUpdate",
    "ChatResponse",
    "ConversationListResponse",
    "ConversationFilter",
    "ConversationStats",
    "MessageRole",
    "MessageType",
    "ConversationStatus"
]