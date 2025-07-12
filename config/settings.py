"""
Configuration Management

This module handles application configuration and environment variables.
"""

import os
from typing import Optional
from pydantic import BaseSettings
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    environment: str = "development"
    debug: bool = True
    secret_key: str = "silver-adventure-secret-key"
    api_version: str = "v1"
    
    # Database
    database_url: str = "sqlite:///./silver_adventure.db"
    database_echo: bool = False
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@silver-adventure.com"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Model
    model_path: str = "models/"
    data_path: str = "data/"
    enable_model_training: bool = True
    
    # Security
    cors_origins: str = "*"
    cors_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_headers: str = "*"
    
    # Performance
    workers: int = 1
    max_requests: int = 1000
    timeout: int = 30
    
    # Feature Flags
    enable_email_sending: bool = True
    enable_churn_prediction: bool = True
    enable_golden_mood_templates: bool = True
    enable_analytics: bool = True
    
    # External Services
    analytics_api_key: str = ""
    monitoring_service_url: str = "http://localhost:9090"
    
    # PyPy
    pypy_enabled: bool = False
    pypy_path: str = "/usr/local/bin/pypy3"
    
    # Development
    reload: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings