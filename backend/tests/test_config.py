"""
Configuration Test Script
Validates that all environment variables are loaded correctly
Run: python scripts/test_config.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings, validate_settings
from app.utils.logger import logger


def test_configuration():
    """Test and display configuration"""
    
    print("\n" + "=" * 60)
    print("🧪 AI PORTFOLIO - CONFIGURATION TEST")
    print("=" * 60 + "\n")
    
    # Test 1: Basic Settings
    print("📋 Basic Settings:")
    print(f"  ✓ App Name: {settings.APP_NAME}")
    print(f"  ✓ Version: {settings.APP_VERSION}")
    print(f"  ✓ Environment: {settings.ENVIRONMENT}")
    print(f"  ✓ Debug: {settings.DEBUG}")
    print()
    
    # Test 2: Security
    print("🔒 Security Settings:")
    print(f"  ✓ Secret Key: {'*' * 20} (length: {len(settings.SECRET_KEY)})")
    print(f"  ✓ JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"  ✓ Admin Username: {settings.ADMIN_USERNAME}")
    print(f"  ✓ Admin Password: {'*' * len(settings.ADMIN_PASSWORD)}")
    print()
    
    # Test 3: OpenAI
    print("🤖 OpenAI Configuration:")
    try:
        print(f"  ✓ API Key: {settings.OPENAI_API_KEY[:10]}...{settings.OPENAI_API_KEY[-4:]}")
        print(f"  ✓ Model: {settings.OPENAI_MODEL}")
        print(f"  ✓ Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
        print(f"  ✓ Max Tokens: {settings.OPENAI_MAX_TOKENS}")
        print(f"  ✓ Temperature: {settings.OPENAI_TEMPERATURE}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 4: MongoDB
    print("🗄️  MongoDB Configuration:")
    try:
        print(f"  ✓ URL: {settings.MONGODB_URL[:30]}...")
        print(f"  ✓ Database: {settings.MONGODB_DB_NAME}")
        print(f"  ✓ Max Connections: {settings.MONGODB_MAX_CONNECTIONS}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 5: Qdrant
    print("🔍 Qdrant Configuration:")
    try:
        print(f"  ✓ URL: {settings.QDRANT_URL}")
        print(f"  ✓ API Key: {settings.QDRANT_API_KEY[:10]}...{settings.QDRANT_API_KEY[-4:]}")
        print(f"  ✓ Collection Prefix: {settings.QDRANT_COLLECTION_PREFIX}")
        print(f"  ✓ Vector Dimension: {settings.VECTOR_DIMENSION}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 6: Rate Limiting
    print("⏱️  Rate Limiting:")
    print(f"  ✓ Session Limit: {settings.RATE_LIMIT_SESSION} requests")
    print(f"  ✓ Daily Limit: {settings.RATE_LIMIT_DAILY} requests")
    print(f"  ✓ Monthly Limit: {settings.RATE_LIMIT_MONTHLY} requests")
    print()
    
    # Test 7: Caching
    print("💾 Cache Configuration:")
    print(f"  ✓ Enabled: {settings.CACHE_ENABLED}")
    print(f"  ✓ TTL: {settings.CACHE_TTL} seconds")
    print(f"  ✓ Max Size: {settings.CACHE_MAX_SIZE}")
    print()
    
    # Test 8: CORS
    print("🌐 CORS Configuration:")
    print(f"  ✓ Allowed Origins: {settings.cors_origins}")
    print()
    
    # Test 9: Logging
    print("📝 Logging Configuration:")
    print(f"  ✓ Level: {settings.LOG_LEVEL}")
    print(f"  ✓ File: {settings.LOG_FILE}")
    print()
    
    # Test 10: Email
    print("📧 Email Configuration:")
    print(f"  ✓ Enabled: {settings.email_enabled}")
    if settings.email_enabled:
        print(f"  ✓ SMTP Host: {settings.SMTP_HOST}")
        print(f"  ✓ Alert Email: {settings.ALERT_EMAIL}")
    else:
        print("  ⚠️  Email not configured (optional)")
    print()
    
    # Test 11: Feature Flags
    print("🚩 Feature Flags:")
    print(f"  - Analytics: {settings.ENABLE_ANALYTICS}")
    print(f"  - Admin CMS: {settings.ENABLE_ADMIN_CMS}")
    print(f"  - Blog: {settings.ENABLE_BLOG}")
    print(f"  - Contact Form: {settings.ENABLE_CONTACT_FORM}")
    print()
    
    # Validate Settings
    print("=" * 60)
    print("🔍 Validating Configuration...")
    print("=" * 60 + "\n")
    
    try:
        validate_settings()
        print("✅ All configuration validated successfully!")
        print()
        return True
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        return False


def test_helper_methods():
    """Test configuration helper methods"""
    
    print("=" * 60)
    print("🧪 Testing Helper Methods")
    print("=" * 60 + "\n")
    
    # Test Qdrant collection name generation
    test_portfolio_id = "test_portfolio_123"
    collection_name = settings.get_qdrant_collection_name(test_portfolio_id)
    print(f"Qdrant Collection Name: {collection_name}")
    
    # Test environment checks
    print(f"Is Production: {settings.is_production()}")
    print(f"Is Development: {settings.is_development()}")
    print()


if __name__ == "__main__":
    """Run configuration tests"""
    
    try:
        # Test configuration loading
        success = test_configuration()
        
        # Test helper methods
        test_helper_methods()
        
        # Final result
        print("=" * 60)
        if success:
            print("✅ CONFIGURATION TEST PASSED")
            logger.info("Configuration test completed successfully")
            sys.exit(0)
        else:
            print("❌ CONFIGURATION TEST FAILED")
            logger.error("Configuration test failed")
            sys.exit(1)
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}\n")
        logger.exception("Configuration test crashed")
        sys.exit(1)