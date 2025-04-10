from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union
import json
import pickle

from redis.asyncio import Redis
import structlog

from app.config.app_config import settings
from app.utils.log_util import get_correlation_id

logger = structlog.get_logger()

T = TypeVar("T")

class AsyncRedisCache:
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._prefix = "cache:"

    async def init(self) -> None:
        """Initialize Redis connection."""
        if not self.redis:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.redis:
            await self.init()
        return await self.redis.get(f"{self._prefix}{key}")

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache with optional TTL."""
        if not self.redis:
            await self.init()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)

        await self.redis.set(
            f"{self._prefix}{key}",
            value,
            ex=ttl,
        )

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if not self.redis:
            await self.init()
        await self.redis.delete(f"{self._prefix}{key}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis:
            await self.init()
        return await self.redis.exists(f"{self._prefix}{key}") > 0

# Global cache instance
cache = AsyncRedisCache()

def cache_response(
    ttl: int = 300,
    key_prefix: str = "",
    skip_kwargs: list[str] = None,
):
    """Cache decorator for FastAPI endpoint responses.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        skip_kwargs: List of kwargs to skip in cache key generation
    
    Usage:
        @router.get("/items/{item_id}")
        @cache_response(ttl=300)
        async def get_item(item_id: int):
            return {"item_id": item_id}
    """
    skip_kwargs = skip_kwargs or []

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            
            # Add args to cache key
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            
            # Add kwargs to cache key
            kwargs_str = ":".join(
                f"{k}={v}"
                for k, v in sorted(kwargs.items())
                if k not in skip_kwargs
            )
            if kwargs_str:
                cache_key += f":{kwargs_str}"

            try:
                # Try to get from cache
                cached_value = await cache.get(cache_key)
                if cached_value:
                    logger.debug(
                        "cache_hit",
                        correlation_id=get_correlation_id(),
                        key=cache_key,
                    )
                    return json.loads(cached_value)

                # If not in cache, execute function
                logger.debug(
                    "cache_miss",
                    correlation_id=get_correlation_id(),
                    key=cache_key,
                )
                result = await func(*args, **kwargs)
                
                # Cache the result
                await cache.set(cache_key, result, ttl)
                return result
            
            except Exception as e:
                logger.error(
                    "cache_error",
                    correlation_id=get_correlation_id(),
                    key=cache_key,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                # On cache error, just execute the function
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator
