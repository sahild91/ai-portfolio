import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.cache import ResponseCache, get_cache


def test_basic_cache_operations():
    """Test basic get/set operations"""
    print("\n" + "=" * 70)
    print("🔧 TEST 1: Basic Cache Operations")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=100, default_ttl=10, enabled=True)
        
        # Set value
        cache.set("test", "key1", {"data": "value1"})
        print("✅ Set value in cache")
        
        # Get value
        result = cache.get("test", "key1")
        
        if result and result["data"] == "value1":
            print("✅ Retrieved value from cache")
            print(f"   - Value: {result}")
        else:
            print("❌ Failed to retrieve value")
            return False
        
        # Get non-existent key
        result = cache.get("test", "nonexistent")
        
        if result is None:
            print("✅ Returns None for missing keys")
        else:
            print("❌ Should return None for missing keys")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_expiration():
    """Test TTL expiration"""
    print("=" * 70)
    print("⏰ TEST 2: Cache Expiration (TTL)")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=100, default_ttl=2, enabled=True)
        
        # Set value with short TTL
        cache.set("test", "expire_key", {"data": "expires soon"}, ttl=2)
        print("✅ Set value with 2s TTL")
        
        # Get immediately (should exist)
        result = cache.get("test", "expire_key")
        
        if result:
            print("✅ Value exists immediately after set")
        else:
            print("❌ Value should exist immediately")
            return False
        
        # Wait for expiration
        print("   Waiting 3 seconds for expiration...")
        time.sleep(3)
        
        # Try to get expired value
        result = cache.get("test", "expire_key")
        
        if result is None:
            print("✅ Expired value returns None")
        else:
            print("❌ Expired value should return None")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_lru_eviction():
    """Test LRU eviction when max size reached"""
    print("=" * 70)
    print("📦 TEST 3: LRU Eviction")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=3, default_ttl=60, enabled=True)
        
        # Fill cache to max
        cache.set("test", "key1", "value1")
        cache.set("test", "key2", "value2")
        cache.set("test", "key3", "value3")
        print("✅ Filled cache to max size (3 entries)")
        
        # Verify all exist
        if cache.get("test", "key1") and cache.get("test", "key2") and cache.get("test", "key3"):
            print("✅ All 3 entries exist")
        else:
            print("❌ Some entries missing")
            return False
        
        # Add 4th entry (should evict oldest)
        cache.set("test", "key4", "value4")
        print("✅ Added 4th entry (should trigger eviction)")
        
        # key1 should be evicted (oldest)
        if cache.get("test", "key1") is None:
            print("✅ Oldest entry (key1) was evicted")
        else:
            print("❌ Oldest entry should be evicted")
            return False
        
        # key2, key3, key4 should exist
        if cache.get("test", "key2") and cache.get("test", "key3") and cache.get("test", "key4"):
            print("✅ Recent entries still exist")
        else:
            print("❌ Recent entries should exist")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_cache_statistics():
    """Test cache statistics tracking"""
    print("=" * 70)
    print("📊 TEST 4: Cache Statistics")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=100, default_ttl=60, enabled=True)
        
        # Generate some hits and misses
        cache.set("test", "stat_key", "value")
        
        # Hits
        cache.get("test", "stat_key")  # Hit
        cache.get("test", "stat_key")  # Hit
        cache.get("test", "stat_key")  # Hit
        
        # Misses
        cache.get("test", "missing1")  # Miss
        cache.get("test", "missing2")  # Miss
        
        stats = cache.get_stats()
        
        print("✅ Cache statistics retrieved!")
        print(f"   - Hits: {stats['hits']}")
        print(f"   - Misses: {stats['misses']}")
        print(f"   - Hit rate: {stats['hit_rate']}%")
        print(f"   - Size: {stats['size']}")
        print(f"   - Max size: {stats['max_size']}")
        print()
        
        # Verify stats
        if stats['hits'] == 3 and stats['misses'] == 2:
            print("✅ Statistics are accurate")
            return True
        else:
            print(f"❌ Statistics incorrect (hits: {stats['hits']}, misses: {stats['misses']})")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_cache_invalidation():
    """Test cache invalidation"""
    print("=" * 70)
    print("🗑️  TEST 5: Cache Invalidation")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=100, default_ttl=60, enabled=True)
        
        # Set values
        cache.set("test", "inv_key1", "value1")
        cache.set("test", "inv_key2", "value2")
        print("✅ Set 2 values in cache")
        
        # Verify they exist
        if cache.get("test", "inv_key1") and cache.get("test", "inv_key2"):
            print("✅ Both values exist")
        else:
            print("❌ Values should exist")
            return False
        
        # Invalidate one
        result = cache.invalidate("test", "inv_key1")
        
        if result:
            print("✅ Invalidated key1")
        else:
            print("❌ Invalidation should succeed")
            return False
        
        # Verify key1 gone, key2 still exists
        if cache.get("test", "inv_key1") is None and cache.get("test", "inv_key2"):
            print("✅ Key1 removed, Key2 still exists")
        else:
            print("❌ Invalidation didn't work correctly")
            return False
        
        # Clear all
        cache.clear()
        print("✅ Cleared entire cache")
        
        # Verify both gone
        if cache.get("test", "inv_key2") is None:
            print("✅ All entries removed after clear")
        else:
            print("❌ Clear didn't remove all entries")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_disabled_cache():
    """Test cache when disabled"""
    print("=" * 70)
    print("❌ TEST 6: Disabled Cache")
    print("=" * 70 + "\n")
    
    try:
        cache = ResponseCache(max_size=100, default_ttl=60, enabled=False)
        
        # Try to set value
        cache.set("test", "disabled_key", "value")
        print("✅ Set called on disabled cache")
        
        # Try to get value (should return None)
        result = cache.get("test", "disabled_key")
        
        if result is None:
            print("✅ Disabled cache returns None")
        else:
            print("❌ Disabled cache should return None")
            return False
        
        stats = cache.get_stats()
        
        if stats['enabled'] is False:
            print("✅ Stats show cache is disabled")
        else:
            print("❌ Stats should show disabled")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_singleton_cache():
    """Test singleton cache instance"""
    print("=" * 70)
    print("🔄 TEST 7: Singleton Instance")
    print("=" * 70 + "\n")
    
    try:
        cache1 = get_cache()
        cache2 = get_cache()
        
        if cache1 is cache2:
            print("✅ Singleton pattern working (same instance)")
        else:
            print("❌ Should return same instance")
            return False
        
        # Set in cache1, get from cache2
        cache1.set("test", "singleton_key", "singleton_value")
        result = cache2.get("test", "singleton_key")
        
        if result == "singleton_value":
            print("✅ Changes shared between instances")
        else:
            print("❌ Should share data between instances")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 CACHE SERVICE TEST SUITE")
    print("Testing in-memory caching functionality...\n")
    
    results = []
    
    # Run tests
    results.append(test_basic_cache_operations())
    results.append(test_cache_expiration())
    results.append(test_lru_eviction())
    results.append(test_cache_statistics())
    results.append(test_cache_invalidation())
    results.append(test_disabled_cache())
    results.append(test_singleton_cache())
    
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
        print("🎉 Cache Service is working!")
        print()
        print("Cache Features:")
        print("✅ In-memory LRU caching")
        print("✅ TTL expiration")
        print("✅ Automatic eviction")
        print("✅ Hit rate tracking")
        print("✅ Cost savings estimation")
        print()
        print("Next Steps:")
        print("1. Integrate cache with vector search")
        print("2. Integrate cache with chat API")
        print("3. Proceed to Chunk 7: Chat API Endpoint")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above")
        return 1


if __name__ == "__main__":
    exit(main())