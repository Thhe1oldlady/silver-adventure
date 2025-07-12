"""Helper utility functions."""

import sys
import time
import functools
from typing import Any, Dict, Callable, Optional, List
from datetime import datetime, timedelta
import importlib

from ..core.logger import get_logger


def safe_import(module_name: str, package: Optional[str] = None) -> Optional[Any]:
    """Safely import a module without raising an exception."""
    try:
        return importlib.import_module(module_name, package)
    except ImportError:
        return None


def retry_on_failure(retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("retry")
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries: {str(e)}")
                        raise
                    
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{retries + 1}), retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
        
        return wrapper
    return decorator


def validate_config(config: Dict[str, Any], required_keys: List[str], optional_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Validate configuration dictionary."""
    errors = []
    
    # Check required keys
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    
    # Check for unexpected keys
    all_valid_keys = set(required_keys)
    if optional_keys:
        all_valid_keys.update(optional_keys)
    
    for key in config:
        if key not in all_valid_keys:
            errors.append(f"Unexpected key: {key}")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return config


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.2f}s"
    else:
        hours = seconds // 3600
        remaining_seconds = seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f}PB"


def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "architecture": sys.maxsize > 2**32 and "64-bit" or "32-bit",
        "pypy": hasattr(sys, 'pypy_version_info'),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add PyPy specific info
    if hasattr(sys, 'pypy_version_info'):
        info["pypy_version"] = sys.pypy_version_info
    
    return info


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Unflatten dictionary."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        d_temp = result
        for part in parts[:-1]:
            if part not in d_temp:
                d_temp[part] = {}
            d_temp = d_temp[part]
        d_temp[parts[-1]] = value
    return result


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def chunked(iterable, chunk_size: int):
    """Yield chunks of specified size from iterable."""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]


def rate_limit(calls_per_second: float):
    """Rate limiting decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator


def memoize(maxsize: int = 128):
    """Memoization decorator with LRU cache."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        access_times = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check cache
            if key in cache:
                access_times[key] = time.time()
                return cache[key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Update cache
            if len(cache) >= maxsize:
                # Remove least recently used item
                lru_key = min(access_times, key=access_times.get)
                del cache[lru_key]
                del access_times[lru_key]
            
            cache[key] = result
            access_times[key] = time.time()
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: (cache.clear(), access_times.clear())
        wrapper.cache_info = lambda: {
            'hits': len(cache),
            'misses': getattr(wrapper, '_misses', 0),
            'maxsize': maxsize,
            'currsize': len(cache)
        }
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0, expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self) -> None:
        """Handle successful execution."""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self) -> None:
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


def timeout(seconds: float):
    """Timeout decorator for functions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set the timeout handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore the old handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator