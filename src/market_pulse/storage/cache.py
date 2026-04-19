import functools
from typing import Any, Callable, TypeVar

import diskcache

from market_pulse.config import settings

F = TypeVar("F", bound=Callable[..., Any])

_cache: diskcache.Cache | None = None


def get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        _cache = diskcache.Cache(str(settings.cache_dir))
    return _cache


def cached(ttl: int | None = None, key_prefix: str = "") -> Callable[[F], F]:
    """Decorator: cache async or sync function results in diskcache."""
    effective_ttl = ttl if ttl is not None else settings.cache_ttl_seconds

    def decorator(func: F) -> F:
        import asyncio

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            cache_key = f"{key_prefix}{func.__name__}:{args}:{sorted(kwargs.items())}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, expire=effective_ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            cache_key = f"{key_prefix}{func.__name__}:{args}:{sorted(kwargs.items())}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire=effective_ttl)
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator
