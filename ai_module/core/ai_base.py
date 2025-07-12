"""
Base AI class providing core functionality for the AI module.

This class serves as the foundation for all AI-related operations in the 
silver adventure repository, providing common methods and properties.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..utils.config import Config


class AIBase:
    """
    Base class for AI functionality providing common methods and properties.
    
    This class establishes the foundation for AI operations including:
    - Configuration management
    - Logging capabilities
    - Common utility methods
    - State management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI base class.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary for AI operations
        """
        self.config = Config(config or {})
        self.logger = self._setup_logger()
        self.created_at = datetime.now()
        self.state = {}
        self.version = "1.0.0"
        
        self.logger.info(f"AIBase initialized with version {self.version}")
    
    def _setup_logger(self) -> logging.Logger:
        """
        Set up logging for the AI module.
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(f"ai_module.{self.__class__.__name__}")
        logger.setLevel(self.config.get("log_level", "INFO"))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the AI instance.
        
        Returns:
            Dict[str, Any]: Status information including version, state, and timestamp
        """
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "state": self.state,
            "config": self.config.get_all()
        }
    
    def update_state(self, key: str, value: Any) -> None:
        """
        Update the internal state of the AI instance.
        
        Args:
            key (str): State key to update
            value (Any): Value to set for the key
        """
        self.state[key] = value
        self.logger.debug(f"State updated: {key} = {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the internal state.
        
        Args:
            key (str): State key to retrieve
            default (Any): Default value if key doesn't exist
            
        Returns:
            Any: Value from state or default
        """
        return self.state.get(key, default)
    
    def reset_state(self) -> None:
        """Reset the internal state to empty."""
        self.state = {}
        self.logger.info("State reset to empty")
    
    def validate_input(self, input_data: Any, expected_type: type = str) -> bool:
        """
        Validate input data against expected type.
        
        Args:
            input_data (Any): Data to validate
            expected_type (type): Expected type for validation
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        if not isinstance(input_data, expected_type):
            self.logger.warning(f"Input validation failed: expected {expected_type}, got {type(input_data)}")
            return False
        return True
    
    def process_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Process and log errors in a standardized way.
        
        Args:
            error (Exception): The error that occurred
            context (str): Additional context about the error
            
        Returns:
            Dict[str, Any]: Error information dictionary
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.error(f"Error in {context}: {error_info}")
        return error_info