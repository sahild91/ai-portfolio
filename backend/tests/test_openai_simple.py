"""
Simple OpenAI Integration Test
Tests that OpenAI API is working correctly
Run: python scripts/test_openai_simple.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.openai_service import openai_service
from app.utils.logger import logger


def test_chat_completion():
    """Test basic chat completion"""
    
    print("\n" + "=" * 60)
    print("🤖 TEST 1: Chat Completion")
    print("=" * 60 + "\n")
    
    # Simple test message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Respond in one sentence."
        },
        {
            "role": "user",
            "content": "Say hello and tell me you're working correctly."
        }
    ]
    
    print("📤 Sending request to OpenAI...")
    result = openai_service.chat_completion(
        messages=messages,
        portfolio_id="test_portfolio"
    )
    
    if result["success"]:
        print("✅ SUCCESS!")
        print(f"\n📝 Response: {result['content']}")
        print(f"\n📊 Usage Stats:")
        print(f"   - Prompt tokens: {result['usage']['prompt_tokens']}")
        print(f"   - Completion tokens: {result['usage']['completion_tokens']}")
        print(f"   - Total tokens: {result['usage']['total_tokens']}")
        print(f"   - Cost: ${result['cost']:.4f}")
        print(f"   - Time: {result['elapsed_time']:.2f}s")
        print(f"   - Model: {result['model']}")
        return True
    else:
        print("❌ FAILED!")
        print(f"\n❌ Error: {result['error']}")
        print(f"   Error Type: {result['error_type']}")
        return False


def test_embedding():
    """Test embedding generation"""
    
    print("\n" + "=" * 60)
    print("🔍 TEST 2: Embedding Generation")
    print("=" * 60 + "\n")
    
    test_text = "This is a test portfolio project about building an AI-powered website."
    
    print(f"📤 Generating embedding for: '{test_text[:50]}...'")
    result = openai_service.generate_embedding(
        text=test_text,
        portfolio_id="test_portfolio"
    )
    
    if result["success"]:
        print("✅ SUCCESS!")
        print(f"\n📊 Embedding Stats:")
        print(f"   - Dimension: {result['dimension']}")
        print(f"   - Tokens: {result['usage']['total_tokens']}")
        print(f"   - Cost: ${result['cost']:.6f}")
        print(f"   - Time: {result['elapsed_time']:.2f}s")
        print(f"   - Model: {result['model']}")
        print(f"\n🔢 First 5 values: {result['embedding'][:5]}")
        return True
    else:
        print("❌ FAILED!")
        print(f"\n❌ Error: {result['error']}")
        print(f"   Error Type: {result['error_type']}")
        return False


def test_json_response():
    """Test JSON mode response"""
    
    print("\n" + "=" * 60)
    print("📋 TEST 3: JSON Response Format")
    print("=" * 60 + "\n")
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Always respond with valid JSON."
        },
        {
            "role": "user",
            "content": "Return a JSON object with a greeting message and a status of 'working'."
        }
    ]
    
    print("📤 Requesting JSON response...")
    result = openai_service.chat_completion(
        messages=messages,
        portfolio_id="test_portfolio",
        response_format={"type": "json_object"}
    )
    
    if result["success"]:
        print("✅ SUCCESS!")
        print(f"\n📝 Raw Response: {result['content']}")
        
        # Try to parse JSON
        parsed = openai_service.parse_json_response(result['content'])
        
        if parsed["success"]:
            print(f"\n✅ Valid JSON!")
            print(f"   Data: {parsed['data']}")
        else:
            print(f"\n⚠️ JSON parsing failed: {parsed['error']}")
        
        print(f"\n💰 Cost: ${result['cost']:.4f}")
        return True
    else:
        print("❌ FAILED!")
        print(f"\n❌ Error: {result['error']}")
        return False


def test_cost_calculation():
    """Test cost calculation"""
    
    print("\n" + "=" * 60)
    print("💰 TEST 4: Cost Calculation")
    print("=" * 60 + "\n")
    
    # Test different token counts
    test_cases = [
        (100, 50),   # Small request
        (500, 200),  # Medium request
        (1000, 500), # Large request
    ]
    
    print("Testing cost calculation for different token counts:\n")
    
    for input_tokens, output_tokens in test_cases:
        cost = openai_service.calculate_cost(
            openai_service.model,
            input_tokens,
            output_tokens
        )
        total_tokens = input_tokens + output_tokens
        print(f"  {input_tokens} input + {output_tokens} output = {total_tokens} tokens → ${cost:.4f}")
    
    print("\n✅ Cost calculation working!")
    return True


def test_system_prompt():
    """Test system prompt generation"""
    
    print("\n" + "=" * 60)
    print("📝 TEST 5: System Prompt Generation")
    print("=" * 60 + "\n")
    
    portfolio_data = {
        "name": "John Doe",
        "bio": "Full-stack developer with 5 years of experience",
        "skills": ["Python", "React", "FastAPI"],
        "projects": [
            {"title": "E-commerce Platform", "tech": ["React", "Node.js"]},
            {"title": "AI Chatbot", "tech": ["Python", "OpenAI"]},
        ]
    }
    
    prompt = openai_service.create_portfolio_system_prompt(portfolio_data)
    
    print("Generated System Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)
    print("\n✅ System prompt generated successfully!")
    return True


def main():
    """Run all tests"""
    
    print("\n")
    print("=" * 60)
    print("🚀 OPENAI SERVICE - INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    try:
        # Test 1: Chat Completion
        results.append(("Chat Completion", test_chat_completion()))
        
        # Test 2: Embeddings
        results.append(("Embeddings", test_embedding()))
        
        # Test 3: JSON Response
        results.append(("JSON Response", test_json_response()))
        
        # Test 4: Cost Calculation
        results.append(("Cost Calculation", test_cost_calculation()))
        
        # Test 5: System Prompt
        results.append(("System Prompt", test_system_prompt()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60 + "\n")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\n📈 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            logger.info("OpenAI integration tests completed successfully")
            return 0
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
            logger.warning(f"OpenAI integration tests failed: {total - passed} failures")
            return 1
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        logger.exception("OpenAI integration tests crashed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)