"""
Application configuration settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings.
    """
    
    # Application
    APP_NAME: str = Field(default="Oracle FastAPI Integration", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    SECRET_KEY: str = Field(default="your-secret-key-change-this", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Oracle Database
    ORACLE_HOST: str = Field(default="localhost", env="ORACLE_HOST")
    ORACLE_PORT: int = Field(default=1521, env="ORACLE_PORT")
    ORACLE_SERVICE: str = Field(default="XEPDB1", env="ORACLE_SERVICE")
    ORACLE_USER: str = Field(default="", env="ORACLE_USER")
    ORACLE_PASSWORD: str = Field(default="", env="ORACLE_PASSWORD")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Machine Learning
    MODEL_PATH: str = Field(default="models/", env="MODEL_PATH")
    ML_CACHE_TTL: int = Field(default=3600, env="ML_CACHE_TTL")
    
    # Network Configuration
    MAX_CONNECTIONS: int = Field(default=100, env="MAX_CONNECTIONS")
    CONNECTION_TIMEOUT: int = Field(default=30, env="CONNECTION_TIMEOUT")
    POOL_SIZE: int = Field(default=20, env="POOL_SIZE")
    POOL_RECYCLE: int = Field(default=3600, env="POOL_RECYCLE")
    
    # Logging
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    LOG_ROTATION: str = Field(default="daily", env="LOG_ROTATION")
    LOG_RETENTION: int = Field(default=30, env="LOG_RETENTION")
    
    @property
    def oracle_dsn(self) -> str:
        """
        Oracle database DSN.
        """
        return f"{self.ORACLE_HOST}:{self.ORACLE_PORT}/{self.ORACLE_SERVICE}"
    
    @property
    def oracle_connection_string(self) -> str:
        """
        Oracle connection string.
        """
        return f"sqlite:///./test.db"  # Use SQLite for testing
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    """
    return Settings()


# Global settings instance
settings = get_settings()