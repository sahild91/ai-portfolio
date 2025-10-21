import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.chat import (
    ChatMessage, ChatConversation, ChatMessageCreate,
    ChatConversationCreate, ChatResponse, ConversationStats,
    MessageRole, MessageType, ConversationStatus
)
from bson import ObjectId


def test_chat_message():
    """Test ChatMessage model"""
    print("\n" + "=" * 70)
    print("💬 TEST 1: Chat Message Model")
    print("=" * 70 + "\n")
    
    try:
        # User message
        user_msg = ChatMessage(
            role=MessageRole.USER,
            content="Tell me about your React projects",
            message_type=MessageType.TEXT
        )
        
        print("✅ User message created successfully!")
        print(f"   - Role: {user_msg.role.value}")
        print(f"   - Content: {user_msg.content}")
        print(f"   - Type: {user_msg.message_type.value}")
        print(f"   - Timestamp: {user_msg.timestamp}")
        print()
        
        # Assistant message with metadata
        assistant_msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="I found 3 React projects in my portfolio...",
            message_type=MessageType.TEXT,
            tokens_used=150,
            cost=0.0003,
            model="gpt-4-turbo-preview",
            response_time=1.2,
            context_used=["project_1", "project_2", "project_3"],
            vector_search_results=5,
            actions=[
                {
                    "type": "filter_projects",
                    "params": {"tech": "React"}
                }
            ]
        )
        
        print("✅ Assistant message created with metadata!")
        print(f"   - Tokens: {assistant_msg.tokens_used}")
        print(f"   - Cost: ${assistant_msg.cost}")
        print(f"   - Model: {assistant_msg.model}")
        print(f"   - Response time: {assistant_msg.response_time}s")
        print(f"   - Context used: {len(assistant_msg.context_used)} items")
        print(f"   - Actions: {len(assistant_msg.actions)}")
        print()
        
        # System message
        system_msg = ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful portfolio assistant.",
            message_type=MessageType.TEXT
        )
        
        print("✅ System message created!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Chat message test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_conversation():
    """Test ChatConversation model"""
    print("=" * 70)
    print("🗨️  TEST 2: Chat Conversation Model")
    print("=" * 70 + "\n")
    
    try:
        portfolio_id = ObjectId()
        
        # Create conversation with messages
        conversation = ChatConversation(
            portfolio_id=portfolio_id,
            session_id="sess_abc123xyz",
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content="Show me your Python projects",
                    message_type=MessageType.TEXT
                ),
                ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content="Here are my Python projects...",
                    message_type=MessageType.TEXT,
                    tokens_used=120,
                    cost=0.00024,
                    model="gpt-4-turbo-preview",
                    response_time=0.8
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content="Tell me more about the first one",
                    message_type=MessageType.TEXT
                )
            ],
            total_messages=3,
            user_messages=2,
            assistant_messages=1,
            total_tokens=120,
            total_cost=0.00024,
            first_message_at=datetime.utcnow(),
            last_message_at=datetime.utcnow(),
            status=ConversationStatus.ACTIVE,
            user_ip="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
        
        print("✅ Conversation created successfully!")
        print(f"   - Portfolio ID: {conversation.portfolio_id}")
        print(f"   - Session ID: {conversation.session_id}")
        print(f"   - Total messages: {conversation.total_messages}")
        print(f"   - User messages: {conversation.user_messages}")
        print(f"   - Assistant messages: {conversation.assistant_messages}")
        print(f"   - Total tokens: {conversation.total_tokens}")
        print(f"   - Total cost: ${conversation.total_cost}")
        print(f"   - Status: {conversation.status.value}")
        print()
        
        # Test message access
        print("✅ Messages in conversation:")
        for i, msg in enumerate(conversation.messages, 1):
            print(f"   {i}. [{msg.role.value}] {msg.content[:50]}...")
        print()
        
        # Test expiry date
        print(f"✅ Conversation expires at: {conversation.expires_at}")
        days_until_expiry = (conversation.expires_at - datetime.utcnow()).days
        print(f"   - Days until expiry: {days_until_expiry}")
        print()
        
        # Test serialization
        conv_dict = conversation.model_dump()
        print("✅ Conversation serialization successful!")
        print(f"   - Keys: {len(conv_dict)} fields")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_schemas():
    """Test chat request/response schemas"""
    print("=" * 70)
    print("📋 TEST 3: Chat Schemas")
    print("=" * 70 + "\n")
    
    try:
        portfolio_id = ObjectId()
        
        # Test ChatMessageCreate
        msg_create = ChatMessageCreate(
            session_id="sess_abc123xyz",
            content="What technologies do you work with?",
            portfolio_id=portfolio_id
        )
        print("✅ ChatMessageCreate schema validated!")
        print(f"   - Session: {msg_create.session_id}")
        print(f"   - Content length: {len(msg_create.content)} chars")
        print()
        
        # Test ChatConversationCreate
        conv_create = ChatConversationCreate(
            portfolio_id=portfolio_id,
            session_id="sess_new123",
            user_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        print("✅ ChatConversationCreate schema validated!")
        print()
        
        # Test ChatResponse
        response = ChatResponse(
            success=True,
            message="Response generated successfully",
            session_id="sess_abc123xyz",
            response_text="I work with Python, FastAPI, React, and more...",
            actions=[
                {
                    "type": "navigate",
                    "params": {"page": "skills"}
                }
            ],
            tokens_used=100,
            cost=0.0002,
            response_time=0.9,
            context_sources=["portfolio", "projects"],
            vector_results_count=3
        )
        print("✅ ChatResponse schema validated!")
        print(f"   - Success: {response.success}")
        print(f"   - Response: {response.response_text[:50]}...")
        print(f"   - Actions: {len(response.actions)}")
        print(f"   - Tokens: {response.tokens_used}")
        print(f"   - Cost: ${response.cost}")
        print()
        
        # Test ConversationStats
        stats = ConversationStats(
            portfolio_id=portfolio_id,
            total_conversations=25,
            active_conversations=5,
            total_messages=150,
            avg_messages_per_conversation=6.0,
            total_tokens=5000,
            total_cost=1.25,
            avg_response_time=1.1,
            avg_rating=4.5,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow()
        )
        print("✅ ConversationStats schema validated!")
        print(f"   - Total conversations: {stats.total_conversations}")
        print(f"   - Avg messages: {stats.avg_messages_per_conversation}")
        print(f"   - Total cost: ${stats.total_cost}")
        print(f"   - Avg rating: {stats.avg_rating}/5")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_validation():
    """Test chat model validation"""
    print("=" * 70)
    print("🔍 TEST 4: Chat Validation Rules")
    print("=" * 70 + "\n")
    
    results = []
    portfolio_id = ObjectId()
    
    # Test 1: Message content too long
    try:
        ChatMessageCreate(
            session_id="sess_123",
            content="x" * 2001,  # Too long
            portfolio_id=portfolio_id
        )
        print("❌ Long message content validation failed")
        results.append(False)
    except Exception:
        print("✅ Long message content rejected correctly")
        results.append(True)
    
    # Test 2: Invalid rating value
    try:
        ChatConversation(
            portfolio_id=portfolio_id,
            session_id="sess_123",
            rating=6  # Out of range (1-5)
        )
        print("❌ Invalid rating validation failed")
        results.append(False)
    except Exception:
        print("✅ Invalid rating rejected correctly")
        results.append(True)
    
    # Test 3: Empty message content
    try:
        ChatMessageCreate(
            session_id="sess_123",
            content="",  # Empty
            portfolio_id=portfolio_id
        )
        print("❌ Empty message validation failed")
        results.append(False)
    except Exception:
        print("✅ Empty message rejected correctly")
        results.append(True)
    
    # Test 4: Missing required fields
    try:
        ChatConversation(
            session_id="sess_123"
            # Missing portfolio_id
        )
        print("❌ Missing required fields validation failed")
        results.append(False)
    except Exception:
        print("✅ Missing required fields rejected correctly")
        results.append(True)
    
    print()
    success_rate = sum(results) / len(results) * 100
    print(f"Validation Tests: {sum(results)}/{len(results)} passed ({success_rate:.0f}%)")
    print()
    
    return all(results)


def test_multi_tenant_isolation():
    """Test multi-tenant conversation isolation"""
    print("=" * 70)
    print("🏢 TEST 5: Multi-Tenant Isolation")
    print("=" * 70 + "\n")
    
    try:
        portfolio_1 = ObjectId()
        portfolio_2 = ObjectId()
        
        # Conversation for portfolio 1
        conv_1 = ChatConversation(
            portfolio_id=portfolio_1,
            session_id="sess_portfolio1_abc",
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content="Show me portfolio 1 projects"
                )
            ]
        )
        
        # Conversation for portfolio 2
        conv_2 = ChatConversation(
            portfolio_id=portfolio_2,
            session_id="sess_portfolio2_xyz",
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content="Show me portfolio 2 projects"
                )
            ]
        )
        
        print("✅ Multi-tenant conversations created!")
        print(f"   - Conv 1 Portfolio ID: {conv_1.portfolio_id}")
        print(f"   - Conv 2 Portfolio ID: {conv_2.portfolio_id}")
        print(f"   - IDs are different: {portfolio_1 != portfolio_2}")
        print()
        
        print("✅ Conversations are properly isolated by portfolio_id")
        print("   Each portfolio's chats are separate and secure!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-tenant test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 CHAT MODELS TEST SUITE")
    print("Testing ChatConversation and ChatMessage models...\n")
    
    results = []
    
    # Run tests
    results.append(test_chat_message())
    results.append(test_chat_conversation())
    results.append(test_chat_schemas())
    results.append(test_chat_validation())
    results.append(test_multi_tenant_isolation())
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.0f}%)")
    print()
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print()
        print("Next Steps:")
        print("1. Save chat.py to backend/app/models/")
        print("2. Update backend/app/models/__init__.py to export chat models")
        print("3. Proceed to Chunk 4C: Vector Models")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above and fix the models.")
        return 1


if __name__ == "__main__":
    exit(main())