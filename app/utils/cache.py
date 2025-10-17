from cachetools import TTLCache, cached
from typing import Callable
from functools import wraps

# cache: key -> value, TTL 600 seconds, maxsize 1024
usda_cache = TTLCache(maxsize=1024, ttl=600)

def cache_usda(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key in usda_cache:
            return usda_cache[key]
        value = func(*args, **kwargs)
        usda_cache[key] = value
        return value
    return wrapper
