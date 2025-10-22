import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.openai_service import OpenAIService
from app.services.vector_search import get_vector_search_service
from app.core.cache import get_cache
from app.models.chat import ChatMessage, MessageRole, MessageType
from app.models.vector_models import VectorSearchRequest, ContentType
from app.utils.logger import logger


class ChatService:
    """
    Chat service that combines vector search with LLM responses
    Handles context retrieval and response generation
    """
    
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.openai_service = OpenAIService()
        self.vector_service = get_vector_search_service()
        self.cache = get_cache()
        
        # System prompt template
        self.system_prompt = """You are a helpful AI assistant for a portfolio website.

Your role:
- Help visitors learn about the portfolio owner's projects and experience
- Answer questions clearly and concisely
- Suggest relevant projects when appropriate
- Be friendly and professional

Guidelines:
- Use the provided context to answer questions accurately
- If you don't have enough information, say so honestly
- Keep responses focused and brief (2-3 sentences unless more detail requested)
- Suggest exploring specific projects when relevant

Available actions you can return:
- navigate: {"type": "navigate", "url": "/projects/project-slug"}
- filter: {"type": "filter", "tech": ["React", "Python"]}
- highlight: {"type": "highlight", "project_id": "123"}

Context provided: {context}
"""
        
        logger.info("ChatService initialized")
    
    def _build_context(
        self,
        portfolio_id: str,
        query: str,
        max_results: int = 3
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Build context from vector search results
        
        Args:
            portfolio_id: Portfolio ID
            query: User query
            max_results: Max search results to include
            
        Returns:
            Tuple of (context_string, context_sources)
        """
        try:
            # Search for relevant content
            search_request = VectorSearchRequest(
                query=query,
                portfolio_id=portfolio_id,
                limit=max_results,
                score_threshold=0.7
            )
            
            search_results = self.vector_service.search(search_request)
            
            if not search_results.success or not search_results.results:
                return "No relevant context found.", []
            
            # Build context string
            context_parts = []
            sources = []
            
            for i, result in enumerate(search_results.results, 1):
                # FIXED: Safely access metadata fields
                metadata = result.metadata or {}
                title = metadata.get("title", "Untitled")
                description = metadata.get("description", result.text_content[:100])
                tech_stack = metadata.get("tech_stack", [])
                url = metadata.get("url", "")
                
                # Build context part
                context_parts.append(
                    f"{i}. {title} ({result.content_type.value})\n"
                    f"   {description}\n"
                    f"   Tech: {', '.join(tech_stack) if tech_stack else 'Not specified'}\n"
                    f"   Relevance: {result.score:.2f}"
                )
                
                # Build source info
                sources.append({
                    "content_id": str(result.content_id),
                    "title": title,
                    "type": result.content_type.value,
                    "url": url,
                    "score": result.score
                })
            
            context_string = "\n\n".join(context_parts)
            
            logger.debug(f"Built context with {len(sources)} sources")
            
            return context_string, sources
            
        except Exception as e:
            logger.error(f"Failed to build context: {e}")
            return "Error retrieving context.", []
    
    def _extract_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Extract action suggestions from LLM response
        
        Args:
            response_text: LLM response text
            
        Returns:
            List of action dicts
        """
        # Simple action extraction (can be enhanced with JSON parsing)
        actions = []
        
        # Check for navigation suggestions
        if "check out" in response_text.lower() or "explore" in response_text.lower():
            # This is a placeholder - in production, LLM would return structured JSON
            pass
        
        return actions
    
    def process_message(
        self,
        query: str,
        portfolio_id: str,
        session_id: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate response
        
        Args:
            query: User query
            portfolio_id: Portfolio ID
            session_id: Session ID
            conversation_history: Previous messages in conversation
            
        Returns:
            Dict with response, actions, metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing chat message for portfolio {portfolio_id}: '{query[:50]}'")
            
            # Check cache first
            cache_key = f"{portfolio_id}:{query}"
            cached = self.cache.get("chat_response", cache_key)
            
            if cached:
                logger.info("Cache hit for chat response")
                cached["from_cache"] = True
                cached["response_time"] = time.time() - start_time
                return cached
            
            # Build context from vector search
            context_string, sources = self._build_context(portfolio_id, query)
            
            # Build conversation messages
            messages = []
            
            # Add system prompt with context
            system_content = self.system_prompt.format(context=context_string)
            messages.append({
                "role": "system",
                "content": system_content
            })
            
            # Add conversation history (last 5 messages)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Generate LLM response
            logger.debug("Calling OpenAI for chat completion")
            llm_result = self.openai_service.chat_completion(
                messages=messages,
                portfolio_id=portfolio_id,
                max_tokens=500,
                temperature=0.7
            )
            
            if not llm_result.get("success"):
                raise Exception(f"LLM call failed: {llm_result.get('error')}")
            
            response_text = llm_result["message"]["content"]
            tokens_used = llm_result["usage"]["total_tokens"]
            cost = llm_result["cost"]
            
            # Extract actions (if any)
            actions = self._extract_actions(response_text)
            
            # Build response
            response = {
                "success": True,
                "response": response_text,
                "actions": actions,
                "context_sources": sources,
                "metadata": {
                    "tokens_used": tokens_used,
                    "cost": cost,
                    "response_time": time.time() - start_time,
                    "context_count": len(sources),
                    "from_cache": False
                }
            }
            
            # Cache the response
            self.cache.set("chat_response", cache_key, response, cost=cost)
            
            logger.info(
                f"Chat response generated in {response['metadata']['response_time']:.2f}s "
                f"(tokens: {tokens_used}, cost: ${cost:.6f})"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, I encountered an error processing your message. Please try again.",
                "actions": [],
                "context_sources": [],
                "metadata": {
                    "tokens_used": 0,
                    "cost": 0.0,
                    "response_time": time.time() - start_time,
                    "context_count": 0,
                    "from_cache": False
                }
            }
    
    def get_suggested_questions(
        self,
        portfolio_id: str
    ) -> List[str]:
        """
        Get suggested questions for a portfolio
        
        Args:
            portfolio_id: Portfolio ID
            
        Returns:
            List of suggested questions
        """
        # Default suggestions (can be customized per portfolio)
        return [
            "What projects have you built?",
            "Tell me about your experience with React",
            "What technologies do you work with?",
            "Show me your most recent projects",
            "What kind of work are you looking for?"
        ]


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create ChatService singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service