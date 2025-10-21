"""
OpenAI Service
Wrapper for OpenAI API with cost tracking and error handling
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from openai import OpenAI, OpenAIError
from app.core.config import settings
from app.utils.logger import logger


class OpenAIService:
    """
    OpenAI API wrapper with built-in cost tracking and error handling
    Provides methods for chat completions and embeddings
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        # Cost tracking (approximate costs per 1K tokens)
        self.costs = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0.0}
        }
        
        logger.info(f"OpenAI Service initialized with model: {self.model}")
    
    def calculate_cost(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int = 0
    ) -> float:
        """
        Calculate estimated cost for API call
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if model not in self.costs:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return 0.0
        
        input_cost = (input_tokens / 1000) * self.costs[model]["input"]
        output_cost = (output_tokens / 1000) * self.costs[model]["output"]
        
        return round(input_cost + output_cost, 6)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        portfolio_id: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion with cost tracking
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            portfolio_id: Portfolio identifier for tracking
            max_tokens: Override default max tokens
            temperature: Override default temperature
            response_format: Optional response format (e.g., {"type": "json_object"})
            
        Returns:
            Dict with response, usage stats, and cost
        """
        start_time = time.time()
        
        try:
            logger.info(f"OpenAI chat completion for portfolio: {portfolio_id}")
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
            }
            
            # Add response format if specified (for JSON mode)
            if response_format:
                request_params["response_format"] = response_format
            
            # Call OpenAI API
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                self.model,
                usage.prompt_tokens,
                usage.completion_tokens
            )
            
            elapsed_time = time.time() - start_time
            
            # Log success
            logger.info(
                f"OpenAI success - Tokens: {usage.total_tokens}, "
                f"Cost: ${cost:.4f}, Time: {elapsed_time:.2f}s"
            )
            
            return {
                "success": True,
                "content": content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "cost": cost,
                "model": self.model,
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except OpenAIError as e:
            elapsed_time = time.time() - start_time
            logger.error(f"OpenAI API error: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time
            }
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.exception(f"Unexpected error in chat completion: {str(e)}")
            
            return {
                "success": False,
                "error": "Internal error occurred",
                "error_type": "UnexpectedError",
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time
            }
    
    def generate_embedding(
        self,
        text: str,
        portfolio_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            portfolio_id: Optional portfolio identifier
            
        Returns:
            Dict with embedding vector, usage stats, and cost
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Generating embedding for text (length: {len(text)})")
            
            # Call OpenAI Embeddings API
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            # Extract embedding vector
            embedding = response.data[0].embedding
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                self.embedding_model,
                usage.total_tokens,
                0
            )
            
            elapsed_time = time.time() - start_time
            
            logger.debug(
                f"Embedding generated - Tokens: {usage.total_tokens}, "
                f"Cost: ${cost:.4f}, Dimension: {len(embedding)}"
            )
            
            return {
                "success": True,
                "embedding": embedding,
                "dimension": len(embedding),
                "usage": {
                    "total_tokens": usage.total_tokens,
                },
                "cost": cost,
                "model": self.embedding_model,
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time
            }
            
        except OpenAIError as e:
            elapsed_time = time.time() - start_time
            logger.error(f"OpenAI embedding error: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time
            }
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.exception(f"Unexpected error in embedding generation: {str(e)}")
            
            return {
                "success": False,
                "error": "Internal error occurred",
                "error_type": "UnexpectedError",
                "portfolio_id": portfolio_id,
                "timestamp": datetime.utcnow().isoformat(),
                "elapsed_time": elapsed_time
            }
    
    def create_portfolio_system_prompt(
        self,
        portfolio_data: Dict[str, Any]
    ) -> str:
        """
        Create system prompt with portfolio context
        
        Args:
            portfolio_data: Portfolio information (projects, bio, etc.)
            
        Returns:
            System prompt string
        """
        # Extract portfolio information
        name = portfolio_data.get("name", "the developer")
        bio = portfolio_data.get("bio", "")
        projects = portfolio_data.get("projects", [])
        skills = portfolio_data.get("skills", [])
        
        # Build system prompt
        prompt = f"""You are an AI assistant for {name}'s portfolio website.

Your role is to help visitors learn about {name}'s work, projects, and skills in a friendly and informative way.

Portfolio Information:
- Bio: {bio}
- Skills: {', '.join(skills) if skills else 'Not specified'}
- Number of projects: {len(projects)}

Instructions:
1. Answer questions about {name}'s projects, skills, and experience
2. Be concise but informative
3. If asked about projects, you can filter and show relevant ones
4. If information is not available, politely say so
5. Maintain a professional yet friendly tone
6. Always respond in valid JSON format with this structure:
   {{"action": "respond", "message": "your response here"}}

Available actions:
- "respond": Simple text response
- "show_projects": Filter and display projects
- "show_contact": Show contact information

Keep responses concise (under 150 words) unless more detail is specifically requested."""

        return prompt
    
    def parse_json_response(
        self,
        content: str
    ) -> Dict[str, Any]:
        """
        Parse JSON response from OpenAI
        
        Args:
            content: Response content string
            
        Returns:
            Parsed JSON dict or error dict
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(content)
            return {
                "success": True,
                "data": parsed
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                try:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "data": parsed
                    }
                except:
                    pass
            
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_content": content
            }


# ============================================
# Global Service Instance
# ============================================

# Create singleton instance
openai_service = OpenAIService()


# ============================================
# Convenience Functions
# ============================================

def chat(
    messages: List[Dict[str, str]],
    portfolio_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for chat completion"""
    return openai_service.chat_completion(messages, portfolio_id, **kwargs)


def embed(text: str, portfolio_id: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for embeddings"""
    return openai_service.generate_embedding(text, portfolio_id)


__all__ = ["openai_service", "chat", "embed", "OpenAIService"]