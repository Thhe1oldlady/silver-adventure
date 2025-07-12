"""Core configuration management for Silver Adventure pipeline."""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# Optional imports with fallbacks
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from pydantic import BaseSettings, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    
    # Fallback base class when pydantic is not available
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def Field(default=None, env=None, **kwargs):
        return default
    
    def validator(field_name, pre=False):
        def decorator(func):
            return func
        return decorator


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    # PostgreSQL
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="silver_adventure", env="POSTGRES_DB")
    
    # MongoDB
    mongo_host: str = Field(default="localhost", env="MONGO_HOST")
    mongo_port: int = Field(default=27017, env="MONGO_PORT")
    mongo_user: str = Field(default="", env="MONGO_USER")
    mongo_password: str = Field(default="", env="MONGO_PASSWORD")
    mongo_db: str = Field(default="silver_adventure", env="MONGO_DB")
    
    # Redis
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        if self.postgres_password:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return f"postgresql://{self.postgres_user}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def mongo_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.mongo_user and self.mongo_password:
            return f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_db}"
        return f"mongodb://{self.mongo_host}:{self.mongo_port}/{self.mongo_db}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class APIConfig(BaseSettings):
    """API configuration settings."""
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="API_DEBUG")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class PipelineConfig(BaseSettings):
    """Pipeline configuration settings."""
    
    # Processing
    batch_size: int = Field(default=1000, env="PIPELINE_BATCH_SIZE")
    max_workers: int = Field(default=4, env="PIPELINE_MAX_WORKERS")
    timeout: int = Field(default=300, env="PIPELINE_TIMEOUT")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="PIPELINE_ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="PIPELINE_METRICS_PORT")
    
    # Caching
    enable_caching: bool = Field(default=True, env="PIPELINE_ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="PIPELINE_CACHE_TTL")
    
    # Performance
    use_pypy: bool = Field(default=False, env="PIPELINE_USE_PYPY")
    enable_profiling: bool = Field(default=False, env="PIPELINE_ENABLE_PROFILING")


class MLConfig(BaseSettings):
    """Machine Learning configuration settings."""
    
    # Model settings
    model_path: str = Field(default="models/", env="ML_MODEL_PATH")
    model_registry_url: str = Field(default="", env="ML_MODEL_REGISTRY_URL")
    
    # Training
    train_batch_size: int = Field(default=32, env="ML_TRAIN_BATCH_SIZE")
    eval_batch_size: int = Field(default=64, env="ML_EVAL_BATCH_SIZE")
    learning_rate: float = Field(default=0.001, env="ML_LEARNING_RATE")
    epochs: int = Field(default=100, env="ML_EPOCHS")
    
    # Inference
    inference_batch_size: int = Field(default=128, env="ML_INFERENCE_BATCH_SIZE")
    model_timeout: int = Field(default=30, env="ML_MODEL_TIMEOUT")
    
    # Churn prediction specific
    churn_model_name: str = Field(default="churn_predictor", env="ML_CHURN_MODEL_NAME")
    churn_threshold: float = Field(default=0.5, env="ML_CHURN_THRESHOLD")


class Config(BaseSettings):
    """Main configuration class combining all settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="silver_adventure.log", env="LOG_FILE")
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    api: APIConfig = APIConfig()
    pipeline: PipelineConfig = PipelineConfig()
    ml: MLConfig = MLConfig()
    
    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @classmethod
    def from_yaml(cls, config_file: str) -> "Config":
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML configuration loading")
        
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "database": self.database.dict() if hasattr(self.database, 'dict') else self.database,
            "api": self.api.dict() if hasattr(self.api, 'dict') else self.api,
            "pipeline": self.pipeline.dict() if hasattr(self.pipeline, 'dict') else self.pipeline,
            "ml": self.ml.dict() if hasattr(self.ml, 'dict') else self.ml,
        }
    
    def save_to_yaml(self, config_file: str) -> None:
        """Save configuration to YAML file."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML configuration saving")
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def reload_config(config_file: Optional[str] = None) -> Config:
    """Reload configuration from file or environment."""
    global config
    if config_file:
        config = Config.from_yaml(config_file)
    else:
        config = Config()
    return config