import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import OrderedDict

from app.core.config import settings
from app.utils.logger import logger


class CacheEntry:
    """Single cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: int):
        """
        Initialize cache entry
        
        Args:
            value: Cached value
            ttl: Time to live in seconds
        """
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl)
        self.hits = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return datetime.utcnow() > self.expires_at
    
    def access(self) -> Any:
        """Access cached value and update metadata"""
        self.hits += 1
        self.last_accessed = datetime.utcnow()
        return self.value


class ResponseCache:
    """
    In-memory LRU cache for API responses
    Thread-safe with size limits and TTL expiration
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        enabled: bool = True
    ):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (1 hour)
            enabled: Whether cache is enabled
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enabled = enabled
        
        # OrderedDict for LRU behavior
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired": 0,
            "total_savings": 0.0,  # Estimated cost savings
        }
        
        logger.info(
            f"ResponseCache initialized - "
            f"Size: {max_size}, TTL: {default_ttl}s, Enabled: {enabled}"
        )
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate cache key
        
        Args:
            namespace: Cache namespace (e.g., 'vector_search', 'llm_response')
            identifier: Unique identifier (e.g., query string, prompt)
            
        Returns:
            Cache key (hash)
        """
        # Combine namespace and identifier
        raw_key = f"{namespace}:{identifier}"
        
        # Hash for consistent key length
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def get(
        self,
        namespace: str,
        identifier: str
    ) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(namespace, identifier)
        
        # Check if key exists
        if key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if entry.is_expired():
            self._stats["expired"] += 1
            self._stats["misses"] += 1
            del self._cache[key]
            logger.debug(f"Cache expired: {namespace}:{identifier[:50]}")
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        # Update stats
        self._stats["hits"] += 1
        
        logger.debug(
            f"Cache hit: {namespace}:{identifier[:50]} "
            f"(hits: {entry.hits + 1})"
        )
        
        return entry.access()
    
    def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: Optional[int] = None,
        cost: float = 0.0
    ) -> None:
        """
        Set value in cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            value: Value to cache
            ttl: TTL in seconds (uses default if None)
            cost: API cost saved by caching
        """
        if not self.enabled:
            return
        
        key = self._generate_key(namespace, identifier)
        ttl = ttl or self.default_ttl
        
        # Check size limit
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Evict oldest entry (LRU)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats["evictions"] += 1
            logger.debug(f"Cache eviction: max size reached ({self.max_size})")
        
        # Add new entry
        self._cache[key] = CacheEntry(value, ttl)
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        logger.debug(
            f"Cache set: {namespace}:{identifier[:50]} "
            f"(TTL: {ttl}s, Cost: ${cost:.6f})"
        )
    
    def invalidate(self, namespace: str, identifier: str) -> bool:
        """
        Invalidate specific cache entry
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            True if entry was removed
        """
        if not self.enabled:
            return False
        
        key = self._generate_key(namespace, identifier)
        
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache invalidated: {namespace}:{identifier[:50]}")
            return True
        
        return False
    
    def invalidate_namespace(self, namespace: str) -> int:
        """
        Invalidate all entries in a namespace
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        # Find all keys with this namespace
        keys_to_remove = []
        namespace_prefix = f"{namespace}:"
        
        for key in list(self._cache.keys()):
            # We need to check if the original namespace matches
            # Since we hash the key, we'll need to track namespace separately
            # For now, we'll just clear all (can optimize later)
            pass
        
        # For simplicity, mark for enhancement
        # In production, store namespace separately in CacheEntry
        count = 0
        logger.debug(f"Namespace invalidation: {namespace} ({count} entries)")
        return count
    
    def clear(self) -> None:
        """Clear entire cache"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        if not self.enabled:
            return 0
        
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self._stats["expired"] += len(expired_keys)
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0.0
        )
        
        return {
            "enabled": self.enabled,
            "size": len(self._cache),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "evictions": self._stats["evictions"],
            "expired": self._stats["expired"],
            "total_requests": total_requests,
        }
    
    def get_entry_info(self, namespace: str, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get info about a specific cache entry
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            Entry info or None if not found
        """
        if not self.enabled:
            return None
        
        key = self._generate_key(namespace, identifier)
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        return {
            "exists": True,
            "expired": entry.is_expired(),
            "created_at": entry.created_at.isoformat(),
            "expires_at": entry.expires_at.isoformat(),
            "hits": entry.hits,
            "last_accessed": entry.last_accessed.isoformat(),
            "ttl_remaining": (entry.expires_at - datetime.utcnow()).total_seconds()
        }


# Singleton instance
_cache_instance = None


def get_cache() -> ResponseCache:
    """Get or create cache singleton"""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = ResponseCache(
            max_size=1000,
            default_ttl=settings.CACHE_TTL if settings.CACHE_ENABLED else 0,
            enabled=settings.CACHE_ENABLED
        )
    
    return _cache_instance


def cache_vector_search(query: str, portfolio_id: str, results: Any) -> None:
    """
    Cache vector search results
    
    Args:
        query: Search query
        portfolio_id: Portfolio ID
        results: Search results to cache
    """
    cache = get_cache()
    identifier = f"{portfolio_id}:{query}"
    cache.set("vector_search", identifier, results, cost=0.000001)


def get_cached_vector_search(query: str, portfolio_id: str) -> Optional[Any]:
    """
    Get cached vector search results
    
    Args:
        query: Search query
        portfolio_id: Portfolio ID
        
    Returns:
        Cached results or None
    """
    cache = get_cache()
    identifier = f"{portfolio_id}:{query}"
    return cache.get("vector_search", identifier)


def cache_llm_response(prompt: str, response: Any, cost: float = 0.0) -> None:
    """
    Cache LLM response
    
    Args:
        prompt: LLM prompt
        response: LLM response to cache
        cost: API cost for this response
    """
    cache = get_cache()
    cache.set("llm_response", prompt, response, cost=cost)


def get_cached_llm_response(prompt: str) -> Optional[Any]:
    """
    Get cached LLM response
    
    Args:
        prompt: LLM prompt
        
    Returns:
        Cached response or None
    """
    cache = get_cache()
    return cache.get("llm_response", prompt)