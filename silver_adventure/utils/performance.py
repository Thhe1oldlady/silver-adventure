"""Performance monitoring and optimization utilities."""

import time
import psutil
import functools
import sys
from typing import Any, Dict, Callable, Optional
from contextlib import contextmanager
import cProfile
import pstats
from io import StringIO

from ..core.logger import get_logger


@contextmanager
def measure_time(operation_name: str = "operation"):
    """Context manager to measure execution time."""
    logger = get_logger("performance")
    start_time = time.time()
    
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"{operation_name} took {duration:.4f} seconds")


def memory_usage() -> Dict[str, float]:
    """Get current memory usage statistics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss / 1024 / 1024,  # MB
        "vms": memory_info.vms / 1024 / 1024,  # MB
        "percent": process.memory_percent(),
        "available": psutil.virtual_memory().available / 1024 / 1024,  # MB
        "total": psutil.virtual_memory().total / 1024 / 1024,  # MB
    }


def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.disable()
            
            # Get stats
            stats_stream = StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            stats.print_stats(10)  # Top 10 functions
            
            logger = get_logger("performance")
            logger.info(f"Profile for {func.__name__}:\n{stats_stream.getvalue()}")
    
    return wrapper


class PyPyOptimizer:
    """Utility class for PyPy optimization."""
    
    def __init__(self):
        self.logger = get_logger("pypy.optimizer")
        self.is_pypy = hasattr(sys, 'pypy_version_info')
    
    def optimize_for_pypy(self, func: Callable) -> Callable:
        """Optimize function for PyPy execution."""
        if not self.is_pypy:
            return func
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Pre-warm JIT for PyPy
            if hasattr(func, '_pypy_warmed'):
                return func(*args, **kwargs)
            
            # Warm up with small data
            try:
                self._warmup_function(func, args, kwargs)
                func._pypy_warmed = True
            except Exception as e:
                self.logger.warning(f"PyPy warmup failed for {func.__name__}: {str(e)}")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def _warmup_function(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """Warm up function for PyPy JIT."""
        # Create smaller versions of arguments for warmup
        warmup_args = self._create_warmup_args(args)
        warmup_kwargs = self._create_warmup_kwargs(kwargs)
        
        # Run function multiple times to trigger JIT
        for _ in range(3):
            try:
                func(*warmup_args, **warmup_kwargs)
            except Exception:
                break  # Stop if warmup fails
    
    def _create_warmup_args(self, args: tuple) -> tuple:
        """Create smaller arguments for warmup."""
        warmup_args = []
        
        for arg in args:
            if hasattr(arg, '__len__') and len(arg) > 100:
                # Use first 10 elements for warmup
                warmup_args.append(arg[:10])
            else:
                warmup_args.append(arg)
        
        return tuple(warmup_args)
    
    def _create_warmup_kwargs(self, kwargs: dict) -> dict:
        """Create smaller keyword arguments for warmup."""
        warmup_kwargs = {}
        
        for key, value in kwargs.items():
            if hasattr(value, '__len__') and len(value) > 100:
                # Use first 10 elements for warmup
                warmup_kwargs[key] = value[:10]
            else:
                warmup_kwargs[key] = value
        
        return warmup_kwargs
    
    def get_pypy_info(self) -> Dict[str, Any]:
        """Get PyPy runtime information."""
        if not self.is_pypy:
            return {"pypy": False}
        
        import sys
        return {
            "pypy": True,
            "version": sys.pypy_version_info,
            "jit_enabled": hasattr(sys, 'pypy_translation_info'),
            "translation_info": getattr(sys, 'pypy_translation_info', {}),
        }


class PerformanceMonitor:
    """Monitor performance metrics."""
    
    def __init__(self):
        self.logger = get_logger("performance.monitor")
        self.metrics = {}
    
    def start_timing(self, operation: str) -> None:
        """Start timing an operation."""
        self.metrics[operation] = {
            "start_time": time.time(),
            "start_memory": memory_usage()
        }
    
    def end_timing(self, operation: str) -> Dict[str, Any]:
        """End timing an operation."""
        if operation not in self.metrics:
            raise ValueError(f"Operation '{operation}' not started")
        
        start_info = self.metrics[operation]
        end_time = time.time()
        end_memory = memory_usage()
        
        duration = end_time - start_info["start_time"]
        memory_delta = end_memory["rss"] - start_info["start_memory"]["rss"]
        
        result = {
            "operation": operation,
            "duration": duration,
            "memory_delta": memory_delta,
            "start_memory": start_info["start_memory"],
            "end_memory": end_memory,
            "timestamp": end_time
        }
        
        self.logger.info(f"Performance: {operation} - {duration:.4f}s, {memory_delta:.2f}MB")
        
        # Clean up
        del self.metrics[operation]
        
        return result
    
    @contextmanager
    def monitor_operation(self, operation: str):
        """Context manager to monitor an operation."""
        self.start_timing(operation)
        try:
            yield
        finally:
            self.end_timing(operation)


# Global instances
pypy_optimizer = PyPyOptimizer()
performance_monitor = PerformanceMonitor()


def get_pypy_optimizer() -> PyPyOptimizer:
    """Get the global PyPy optimizer instance."""
    return pypy_optimizer


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor