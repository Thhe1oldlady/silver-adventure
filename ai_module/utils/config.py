"""
Configuration management for AI module.

This module provides configuration management capabilities including
loading, validation, and accessing configuration parameters.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path


class Config:
    """
    Configuration management class for AI module.
    
    This class handles loading, validation, and accessing configuration
    parameters from various sources including files, environment variables,
    and direct dictionary input.
    """
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_data (Optional[Dict[str, Any]]): Initial configuration data
        """
        self._config = {}
        self._defaults = self._load_defaults()
        
        # Load configuration from various sources
        self._load_from_defaults()
        
        if config_data:
            self._load_from_dict(config_data)
    
    def _load_defaults(self) -> Dict[str, Any]:
        """
        Load default configuration values.
        
        Returns:
            Dict[str, Any]: Default configuration dictionary
        """
        return {
            "log_level": "INFO",
            "max_history_length": 100,
            "max_response_length": 1000,
            "enable_sentiment_analysis": True,
            "enable_keyword_extraction": True,
            "enable_text_summarization": True,
            "default_max_keywords": 10,
            "default_summary_sentences": 3,
            "text_processing": {
                "remove_stopwords": True,
                "min_keyword_length": 3,
                "max_keyword_frequency": 0.5
            },
            "user_interaction": {
                "greeting_enabled": True,
                "help_enabled": True,
                "command_prefix": "/",
                "session_timeout": 3600  # 1 hour in seconds
            },
            "ai_base": {
                "state_persistence": False,
                "error_reporting": True,
                "debug_mode": False
            }
        }
    
    def _load_from_defaults(self) -> None:
        """Load configuration from default values."""
        self._config.update(self._defaults)
    
    def _load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Load configuration from dictionary.
        
        Args:
            config_dict (Dict[str, Any]): Configuration dictionary
        """
        self._deep_update(self._config, config_dict)
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep update dictionary with another dictionary.
        
        Args:
            target (Dict[str, Any]): Target dictionary to update
            source (Dict[str, Any]): Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            file_path (Union[str, Path]): Path to configuration file
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._load_from_dict(config_data)
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in configuration file: {file_path}", e.doc, e.pos)
    
    def load_from_env(self, prefix: str = "AI_MODULE_") -> None:
        """
        Load configuration from environment variables.
        
        Args:
            prefix (str): Prefix for environment variables
        """
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                
                # Try to parse as JSON first, then as string
                try:
                    env_config[config_key] = json.loads(value)
                except json.JSONDecodeError:
                    env_config[config_key] = value
        
        if env_config:
            self._load_from_dict(env_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key (str): Configuration key (supports dot notation)
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key (str): Configuration key (supports dot notation)
            value (Any): Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dict[str, Any]: Complete configuration dictionary
        """
        return self._config.copy()
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key (str): Configuration key (supports dot notation)
            
        Returns:
            bool: True if key exists, False otherwise
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False
    
    def update(self, config_data: Dict[str, Any]) -> None:
        """
        Update configuration with new data.
        
        Args:
            config_data (Dict[str, Any]): New configuration data
        """
        self._load_from_dict(config_data)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = {}
        self._load_from_defaults()
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Save current configuration to JSON file.
        
        Args:
            file_path (Union[str, Path]): Path to save configuration
        """
        file_path = Path(file_path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate current configuration.
        
        Returns:
            Dict[str, Any]: Validation results with any issues found
        """
        issues = []
        
        # Check required keys
        required_keys = ["log_level", "max_history_length", "max_response_length"]
        for key in required_keys:
            if not self.has(key):
                issues.append(f"Missing required configuration key: {key}")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.get("log_level") not in valid_log_levels:
            issues.append(f"Invalid log_level: {self.get('log_level')}. Must be one of {valid_log_levels}")
        
        # Validate numeric values
        numeric_keys = ["max_history_length", "max_response_length", "default_max_keywords", "default_summary_sentences"]
        for key in numeric_keys:
            value = self.get(key)
            if value is not None and not isinstance(value, (int, float)):
                issues.append(f"Configuration key '{key}' must be numeric, got: {type(value).__name__}")
            elif value is not None and value < 0:
                issues.append(f"Configuration key '{key}' must be non-negative, got: {value}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config({json.dumps(self._config, indent=2)})"
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self._config, indent=2)