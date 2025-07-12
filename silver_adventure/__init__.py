"""
Silver Adventure - PyPy-optimized pipeline system for data processing and AI integration.

This package provides a comprehensive pipeline system with the following features:
- Modular and scalable pipeline architecture
- PyPy optimization for performance-critical components
- FastAPI integration for web services
- AI/ML model integration including churn prediction
- Database integration with Oracle and other systems
- Monitoring and observability tools
- Comprehensive testing framework

Components:
- api: FastAPI web services and endpoints
- core: Core pipeline framework and configuration
- ml: Machine learning models and utilities
- pipeline: Data processing pipeline components
- utils: Utility functions and helpers
"""

__version__ = "0.1.0"
__author__ = "Silver Adventure Team"
__email__ = "team@silver-adventure.com"
__description__ = "A PyPy-optimized pipeline system for data processing and AI integration"

# Package-level imports for easy access
from .core.config import Config
from .core.pipeline import Pipeline
from .core.logger import get_logger

# Export main classes
__all__ = [
    "Config",
    "Pipeline", 
    "get_logger",
]

# Version information
VERSION_INFO = {
    "major": 0,
    "minor": 1,
    "patch": 0,
    "release": "alpha",
    "build": 1
}

def get_version():
    """Get the version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()