"""
OpenAI Service - Pytest Tests
Unit tests for OpenAI integration
Run: pytest tests/test_openai.py -v
"""

import pytest
from app.services.openai_service import OpenAIService, openai_service


class TestOpenAIService:
    """Test suite for OpenAI service"""
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        service = OpenAIService()
        
        assert service.client is not None
        assert service.model is not None
        assert service.embedding_model is not None
        assert isinstance(service.costs, dict)
    
    def test_cost_calculation(self):
        """Test cost calculation for different models"""
        service = OpenAIService()
        
        # Test GPT-4 cost
        cost = service.calculate_cost("gpt-4", 1000, 500)
        assert cost > 0
        assert isinstance(cost, float)
        
        # Test GPT-3.5 cost (should be cheaper)
        cost_35 = service.calculate_cost("gpt-3.5-turbo", 1000, 500)
        assert cost_35 < cost
        
        # Test embedding cost
        embed_cost = service.calculate_cost("text-embedding-ada-002", 1000, 0)
        assert embed_cost > 0
        assert embed_cost < cost_35
    
    def test_system_prompt_generation(self):
        """Test system prompt generation"""
        service = OpenAIService()
        
        portfolio_data = {
            "name": "Test Developer",
            "bio": "A skilled developer",
            "skills": ["Python", "JavaScript"],
            "projects": [{"title": "Test Project"}]
        }
        
        prompt = service.create_portfolio_system_prompt(portfolio_data)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Test Developer" in prompt
        assert "Python" in prompt
    
    def test_json_parsing_success(self):
        """Test JSON response parsing - success case"""
        service = OpenAIService()
        
        valid_json = '{"action": "respond", "message": "Hello!"}'
        result = service.parse_json_response(valid_json)
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["action"] == "respond"
    
    def test_json_parsing_failure(self):
        """Test JSON response parsing - failure case"""
        service = OpenAIService()
        
        invalid_json = "This is not JSON"
        result = service.parse_json_response(invalid_json)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_json_parsing_markdown(self):
        """Test JSON extraction from markdown code blocks"""
        service = OpenAIService()
        
        markdown_json = '```json\n{"status": "ok"}\n```'
        result = service.parse_json_response(markdown_json)
        
        assert result["success"] is True
        assert result["data"]["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_chat_completion_structure(self):
        """Test chat completion response structure"""
        # We won't actually call the API in unit tests
        # Just verify the method exists and has correct signature
        service = OpenAIService()
        
        assert hasattr(service, 'chat_completion')
        assert callable(service.chat_completion)
    
    @pytest.mark.asyncio
    async def test_embedding_structure(self):
        """Test embedding generation response structure"""
        service = OpenAIService()
        
        assert hasattr(service, 'generate_embedding')
        assert callable(service.generate_embedding)
    
    def test_singleton_instance(self):
        """Test that global instance is available"""
        assert openai_service is not None
        assert isinstance(openai_service, OpenAIService)


# Integration tests (these actually call OpenAI API)
@pytest.mark.integration
class TestOpenAIIntegration:
    """Integration tests that call real OpenAI API"""
    
    @pytest.mark.skip(reason="Requires OpenAI API call - run manually")
    def test_real_chat_completion(self):
        """Test real chat completion (skip by default to save costs)"""
        messages = [
            {"role": "user", "content": "Say 'test successful' in exactly those words."}
        ]
        
        result = openai_service.chat_completion(
            messages=messages,
            portfolio_id="pytest_test"
        )
        
        assert result["success"] is True
        assert "content" in result
        assert "usage" in result
        assert "cost" in result
    
    @pytest.mark.skip(reason="Requires OpenAI API call - run manually")
    def test_real_embedding(self):
        """Test real embedding generation (skip by default to save costs)"""
        result = openai_service.generate_embedding(
            text="Test embedding text",
            portfolio_id="pytest_test"
        )
        
        assert result["success"] is True
        assert "embedding" in result
        assert result["dimension"] == 1536
        assert "cost" in result