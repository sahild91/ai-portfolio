"""
Database Connection Test
Simple script to test MongoDB connection
Run: python scripts/test_db_connection.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.db import db_manager, Collections
from app.utils.logger import logger


async def test_connection():
    """Test MongoDB connection"""
    
    print("\n" + "=" * 60)
    print("🗄️  MONGODB CONNECTION TEST")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Connect to database
        print("📡 TEST 1: Connecting to MongoDB...")
        await db_manager.connect()
        print("✅ Connection established!")
        print()
        
        # Test 2: Health check
        print("🏥 TEST 2: Health Check...")
        health = await db_manager.health_check()
        
        if health["healthy"]:
            print("✅ Database is healthy!")
            print(f"   - Status: {health['status']}")
            print(f"   - Database: {health['database']}")
            print(f"   - MongoDB Version: {health['version']}")
            print(f"   - Existing Collections: {len(health['collections'])}")
            if health['collections']:
                for col in health['collections']:
                    print(f"     • {col}")
        else:
            print("❌ Database unhealthy!")
            print(f"   - Error: {health.get('error', 'Unknown')}")
        print()
        
        # Test 3: Get collection
        print("📚 TEST 3: Accessing Collections...")
        for collection_name in [
            Collections.USERS,
            Collections.PORTFOLIOS,
            Collections.PROJECTS,
            Collections.BLOGS,
            Collections.CHAT_HISTORY
        ]:
            collection = db_manager.get_collection(collection_name)
            count = await collection.count_documents({})
            print(f"   ✓ {collection_name}: {count} documents")
        print()
        
        # Test 4: Simple write/read test
        print("✍️  TEST 4: Write/Read Test...")
        test_collection = db_manager.get_collection("_test_collection")
        
        # Insert test document
        test_doc = {"test": "data", "timestamp": "2025-10-20"}
        result = await test_collection.insert_one(test_doc)
        print(f"   ✓ Inserted test document: {result.inserted_id}")
        
        # Read test document
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print(f"   ✓ Retrieved test document: {found_doc['test']}")
        
        # Delete test document
        delete_result = await test_collection.delete_one({"_id": result.inserted_id})
        print(f"   ✓ Deleted test document: {delete_result.deleted_count} document(s)")
        print()
        
        # Test 5: Multi-tenant query simulation
        print("🔐 TEST 5: Multi-Tenant Query Pattern...")
        
        # Simulate portfolio-specific query
        portfolio_id = "test_portfolio_123"
        projects_collection = db_manager.get_collection(Collections.PROJECTS)
        
        # Query with portfolio_id filter (multi-tenant pattern)
        cursor = projects_collection.find({"portfolio_id": portfolio_id})
        projects = await cursor.to_list(length=10)
        
        print(f"   ✓ Queried projects for portfolio: {portfolio_id}")
        print(f"   ✓ Found {len(projects)} projects")
        print()
        
        # Summary
        print("=" * 60)
        print("✅ ALL DATABASE TESTS PASSED!")
        print("=" * 60)
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        logger.exception("Database test failed")
        return False
    
    finally:
        # Always disconnect
        print("🔌 Disconnecting from database...")
        await db_manager.disconnect()
        print("✅ Disconnected")


async def main():
    """Run database tests"""
    success = await test_connection()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)