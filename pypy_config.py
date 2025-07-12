# PyPy Configuration for Silver Adventure Pipeline

## PyPy Compatibility Settings
# This file contains configuration for running Silver Adventure with PyPy
# for improved performance in computational tasks

# PyPy Installation Notes:
# 1. Install PyPy3.9 via conda: conda install -c conda-forge pypy3.9
# 2. Or download from: https://www.pypy.org/download.html
# 3. Create PyPy virtual environment: pypy3 -m venv pypy-env

# Performance Optimization Flags
PYPY_GC_NURSERY_SIZE = "32MB"
PYPY_GC_MAJOR_COLLECT = "1.5"
PYPY_GC_MEMORY_PRESSURE = "1.0"

# JIT Compilation Settings
PYPY_JIT_ENABLE = "1"
PYPY_JIT_THRESHOLD = "1039"
PYPY_JIT_FUNCTION_THRESHOLD = "1619"

# Memory Management
PYPY_GC_MIN = "4MB"
PYPY_GC_MAX = "2GB"

# Logging Configuration
PYPY_LOG_FILE = "pypy_performance.log"
PYPY_JIT_LOG = "jit_compilation.log"

# Compatible Modules List
# These modules are tested and verified to work with PyPy
PYPY_COMPATIBLE_MODULES = [
    "numpy",
    "pandas",
    "scipy",
    "scikit-learn",
    "fastapi",
    "uvicorn",
    "httpx",
    "requests",
    "sqlalchemy",
    "pydantic",
    "python-dotenv",
    "pyyaml",
    "prometheus-client",
    "asyncpg",
    "aioredis",
    "celery",
    "redis",
]

# Modules with Limited PyPy Support
# These modules may have reduced functionality or performance with PyPy
PYPY_LIMITED_MODULES = [
    "tensorflow",  # Limited support, use with caution
    "torch",       # Limited support, use with caution
    "matplotlib",  # May be slower than CPython
    "seaborn",     # May be slower than CPython
]

# Incompatible Modules
# These modules are not recommended for use with PyPy
PYPY_INCOMPATIBLE_MODULES = [
    "psycopg2",    # Use psycopg2-binary instead
    "pymongo",     # Limited C extension support
    "numba",       # JIT compilation conflicts
    "cython",      # C extension conflicts
]

# Environment Variables for PyPy Optimization
# Set these in your environment or docker configuration
ENVIRONMENT_VARIABLES = {
    "PYPY_GC_NURSERY_SIZE": "32MB",
    "PYPY_GC_MAJOR_COLLECT": "1.5", 
    "PYPY_GC_MEMORY_PRESSURE": "1.0",
    "PYPY_JIT_ENABLE": "1",
    "PYPY_JIT_THRESHOLD": "1039",
    "PYPY_JIT_FUNCTION_THRESHOLD": "1619",
    "PYPY_GC_MIN": "4MB",
    "PYPY_GC_MAX": "2GB"
}

# Performance Benchmarking Configuration
BENCHMARK_CONFIG = {
    "enable_profiling": True,
    "profile_output_dir": "profiles/",
    "benchmark_iterations": 100,
    "warmup_iterations": 10,
    "memory_tracking": True,
    "jit_tracking": True
}

# Pipeline Component PyPy Compatibility
PIPELINE_COMPONENT_COMPATIBILITY = {
    "data_processing": "full",      # Full PyPy support
    "ml_inference": "partial",      # Some models may not support PyPy
    "api_server": "full",          # Full PyPy support
    "database_ops": "full",        # Full PyPy support with compatible drivers
    "caching": "full",             # Full PyPy support
    "monitoring": "full",          # Full PyPy support
}

# Recommended PyPy Usage Patterns
USAGE_PATTERNS = {
    "cpu_intensive": "highly_recommended",
    "io_bound": "recommended",
    "memory_intensive": "recommended",
    "ml_training": "not_recommended",
    "ml_inference": "conditionally_recommended",
    "api_serving": "highly_recommended",
    "data_processing": "highly_recommended",
}