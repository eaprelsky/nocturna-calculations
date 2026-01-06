"""
Redis cache manager for the Nocturna Calculations API.
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis
from .config import settings

class RedisCache:
    """Redis cache manager for storing and retrieving cached data."""
    
    def __init__(self):
        """Initialize Redis connection pool."""
        # Initialize Redis connection pool using settings (attributes are uppercase)
        self.pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
        )
        self.redis = redis.Redis(connection_pool=self.pool)
        # Prefix for all cache keys to avoid collisions
        self.prefix = getattr(settings, "CACHE_PREFIX", "calc:")
    
    def _get_key(self, key: str) -> str:
        """Get full cache key with prefix."""
        return f"{self.prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.redis.get(self._get_key(key))
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            if ttl is None:
                ttl = settings.CACHE_TTL
            
            data = pickle.dumps(value)
            return self.redis.setex(
                self._get_key(key),
                ttl,
                data
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis.delete(self._get_key(key)))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis.exists(self._get_key(key)))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries with the prefix."""
        try:
            keys = self.redis.keys(f"{self.prefix}*")
            if keys:
                return bool(self.redis.delete(*keys))
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def get_or_set(
        self,
        key: str,
        default_func: callable,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> Any:
        """Get value from cache or set it using default_func if not exists."""
        value = self.get(key)
        if value is None:
            value = default_func()
            self.set(key, value, ttl)
        return value

# Create global cache instance
cache = RedisCache() 