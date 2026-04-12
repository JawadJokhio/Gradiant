from functools import wraps
from typing import Callable, Any

# Simple in-memory cache
_FUNCTION_CACHE = {}

def memoize(func: Callable) -> Callable:
    """
    Decorator for simple in-memory caching of function calls based on arguments.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key using args and kwargs
        # Convert mutable arguments to string representation for basic hashing
        key = (func.__name__, str(args), str(kwargs))
        if key not in _FUNCTION_CACHE:
            _FUNCTION_CACHE[key] = func(*args, **kwargs)
        return _FUNCTION_CACHE[key]
    return wrapper

def clear_cache():
    """Clear all cached responses."""
    _FUNCTION_CACHE.clear()
