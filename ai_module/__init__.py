"""
AI Module for Silver Adventure Repository

This module provides AI-based functionalities for the silver adventure repository,
including text processing, user interaction handling, and core AI capabilities.

Author: AI Assistant
Version: 1.0.0
"""

from .core.ai_base import AIBase
from .core.text_processor import TextProcessor
from .core.user_interaction import UserInteraction
from .utils.config import Config
from .utils.helpers import Helper

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

# Main exports
__all__ = [
    "AIBase",
    "TextProcessor", 
    "UserInteraction",
    "Config",
    "Helper"
]