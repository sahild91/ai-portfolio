"""
Test Pydantic Models
Validates model creation and serialization
Run: python scripts/test_models.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.user import User, UserCreate, UserResponse
from app.models.portfolio import Portfolio, PortfolioCreate, PortfolioSettings
from bson import ObjectId


def test_user_model():
    """Test User model"""
    print("\n" + "=" * 60)
    print("👤 TEST 1: User Model")
    print("=" * 60 + "\n")
    
    try:
        # Create a user
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password_here",
            full_name="Test User",
            subscription_tier="free"
        )
        
        print("✅ User model created successfully!")
        print(f"   - Email: {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Created at: {user.created_at}")
        print()
        
        # Test serialization
        user_dict = user.model_dump()
        print("✅ User serialization successful!")
        print(f"   - Keys: {list(user_dict.keys())}")
        print()
        
        # Test UserCreate schema
        user_create = UserCreate(
            email="new@example.com",
            username="newuser",
            password="securepassword123",
            full_name="New User"
        )
        print("✅ UserCreate schema validated!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        return False


def test_portfolio_model():
    """Test Portfolio model"""
    print("=" * 60)
    print("📁 TEST 2: Portfolio Model")
    print("=" * 60 + "\n")
    
    try:
        # Create a portfolio
        owner_id = ObjectId()
        
        portfolio = Portfolio(
            owner_id=owner_id,
            subdomain="testportfolio",
            display_name="Test Portfolio",
            tagline="Full-Stack Developer",
            bio="This is a test bio",
            skills=["Python", "JavaScript", "React"],
            is_published=True
        )
        
        print("✅ Portfolio model created successfully!")
        print(f"   - Subdomain: {portfolio.subdomain}")
        print(f"   - Display Name: {portfolio.display_name}")
        print(f"   - Skills: {', '.join(portfolio.skills)}")
        print(f"   - Published: {portfolio.is_published}")
        print()
        
        # Test settings
        print("✅ Portfolio settings:")
        print(f"   - Theme: {portfolio.settings.theme}")
        print(f"   - Chat Enabled: {portfolio.settings.chat_enabled}")
        print(f"   - Chat Greeting: {portfolio.settings.chat_greeting[:50]}...")
        print()
        
        # Test serialization
        portfolio_dict = portfolio.model_dump()
        print("✅ Portfolio serialization successful!")
        print(f"   - Keys: {list(portfolio_dict.keys())[:8]}...")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio model test failed: {e}")
        return False


def test_portfolio_settings():
    """Test PortfolioSettings model"""
    print("=" * 60)
    print("⚙️  TEST 3: Portfolio Settings")
    print("=" * 60 + "\n")
    
    try:
        settings = PortfolioSettings(
            theme="dark",
            primary_color="#1E3A8A",
            chat_enabled=True,
            analytics_enabled=True,
            google_analytics_id="GA-123456",
            meta_title="My Portfolio",
            meta_description="Full-stack developer portfolio"
        )
        
        print("✅ Portfolio settings created!")
        print(f"   - Theme: {settings.theme}")
        print(f"   - Primary Color: {settings.primary_color}")
        print(f"   - Chat Enabled: {settings.chat_enabled}")
        print(f"   - Analytics Enabled: {settings.analytics_enabled}")
        print(f"   - Meta Title: {settings.meta_title}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


def test_model_validation():
    """Test model validation"""
    print("=" * 60)
    print("🔍 TEST 4: Model Validation")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Invalid email
    try:
        UserCreate(
            email="invalid-email",
            username="testuser",
            password="password123"
        )
        print("❌ Invalid email validation failed")
        results.append(False)
    except Exception:
        print("✅ Invalid email rejected correctly")
        results.append(True)
    
    # Test 2: Short username
    try:
        UserCreate(
            email="test@example.com",
            username="ab",  # Too short
            password="password123"
        )
        print("❌ Short username validation failed")
        results.append(False)
    except Exception:
        print("✅ Short username rejected correctly")
        results.append(True)
    
    # Test 3: Short password
    try:
        UserCreate(
            email="test@example.com",
            username="testuser",
            password="short"  # Too short
        )
        print("❌ Short password validation failed")
        results.append(False)
    except Exception:
        print("✅ Short password rejected correctly")
        results.append(True)
    
    # Test 4: Missing required fields
    try:
        Portfolio(
            subdomain="test"
            # Missing owner_id and display_name
        )
        print("❌ Required field validation failed")
        results.append(False)
    except Exception:
        print("✅ Missing required fields rejected correctly")
        results.append(True)
    
    print()
    return all(results)


def main():
    """Run all model tests"""
    
    print("\n")
    print("=" * 60)
    print("🧪 PYDANTIC MODELS TEST")
    print("=" * 60)
    
    results = []
    
    try:
        # Run tests
        results.append(("User Model", test_user_model()))
        results.append(("Portfolio Model", test_portfolio_model()))
        results.append(("Portfolio Settings", test_portfolio_settings()))
        results.append(("Model Validation", test_model_validation()))
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60 + "\n")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\n📈 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL MODEL TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
            return 1
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)