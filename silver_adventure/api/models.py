"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineRequest(BaseModel):
    """Request model for pipeline execution."""
    
    pipeline_name: str = Field(..., description="Name of the pipeline to execute")
    data: Any = Field(..., description="Input data for the pipeline")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Pipeline configuration")
    async_execution: bool = Field(default=False, description="Execute pipeline asynchronously")
    
    class Config:
        schema_extra = {
            "example": {
                "pipeline_name": "data_processing",
                "data": {"input": "sample data"},
                "config": {"batch_size": 1000},
                "async_execution": False
            }
        }


class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""
    
    pipeline_name: str = Field(..., description="Name of the executed pipeline")
    execution_id: str = Field(..., description="Unique execution identifier")
    status: PipelineStatus = Field(..., description="Execution status")
    result: Optional[Any] = Field(default=None, description="Pipeline result data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    errors: List[str] = Field(default_factory=list, description="Execution errors")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: Optional[datetime] = Field(default=None, description="Execution end time")
    duration: Optional[float] = Field(default=None, description="Execution duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "pipeline_name": "data_processing",
                "execution_id": "exec_123456",
                "status": "completed",
                "result": {"output": "processed data"},
                "metadata": {"steps_executed": 5},
                "errors": [],
                "start_time": "2023-01-01T00:00:00Z",
                "end_time": "2023-01-01T00:01:00Z",
                "duration": 60.0
            }
        }


class ChurnPredictionRequest(BaseModel):
    """Request model for churn prediction."""
    
    customer_id: str = Field(..., description="Customer identifier")
    features: Dict[str, Union[str, int, float]] = Field(..., description="Customer features")
    model_version: Optional[str] = Field(default=None, description="Model version to use")
    
    @validator('features')
    def validate_features(cls, v):
        """Validate customer features."""
        required_features = [
            'tenure', 'monthly_charges', 'total_charges', 'contract_type',
            'payment_method', 'internet_service', 'phone_service'
        ]
        
        for feature in required_features:
            if feature not in v:
                raise ValueError(f"Required feature '{feature}' missing")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "customer_id": "CUST_001",
                "features": {
                    "tenure": 12,
                    "monthly_charges": 79.99,
                    "total_charges": 959.88,
                    "contract_type": "Month-to-month",
                    "payment_method": "Credit card",
                    "internet_service": "Fiber optic",
                    "phone_service": "Yes"
                },
                "model_version": "v1.0"
            }
        }


class ChurnPredictionResponse(BaseModel):
    """Response model for churn prediction."""
    
    customer_id: str = Field(..., description="Customer identifier")
    churn_probability: float = Field(..., description="Probability of churn (0-1)")
    churn_prediction: bool = Field(..., description="Binary churn prediction")
    risk_level: str = Field(..., description="Risk level (low, medium, high)")
    model_version: str = Field(..., description="Model version used")
    prediction_time: datetime = Field(..., description="Prediction timestamp")
    feature_importance: Dict[str, float] = Field(default_factory=dict, description="Feature importance scores")
    
    @validator('churn_probability')
    def validate_probability(cls, v):
        """Validate probability is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Churn probability must be between 0 and 1")
        return v
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Validate risk level."""
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "customer_id": "CUST_001",
                "churn_probability": 0.75,
                "churn_prediction": True,
                "risk_level": "high",
                "model_version": "v1.0",
                "prediction_time": "2023-01-01T00:00:00Z",
                "feature_importance": {
                    "tenure": 0.25,
                    "monthly_charges": 0.20,
                    "total_charges": 0.15
                }
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Uptime in seconds")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00Z",
                "version": "0.1.0",
                "uptime": 3600.0,
                "dependencies": {
                    "database": "healthy",
                    "cache": "healthy",
                    "ml_service": "healthy"
                }
            }
        }


class MetricsResponse(BaseModel):
    """Response model for metrics."""
    
    timestamp: datetime = Field(..., description="Metrics timestamp")
    metrics: Dict[str, float] = Field(..., description="Metrics data")
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2023-01-01T00:00:00Z",
                "metrics": {
                    "pipeline_executions_total": 1000,
                    "pipeline_duration_avg": 45.5,
                    "prediction_requests_total": 2000,
                    "prediction_accuracy": 0.85
                }
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""
    
    customers: List[Dict[str, Union[str, int, float]]] = Field(..., description="List of customer data")
    model_version: Optional[str] = Field(default=None, description="Model version to use")
    return_probabilities: bool = Field(default=True, description="Return prediction probabilities")
    
    @validator('customers')
    def validate_customers(cls, v):
        """Validate customer data."""
        if not v:
            raise ValueError("At least one customer required")
        
        if len(v) > 1000:
            raise ValueError("Maximum 1000 customers per batch")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "customers": [
                    {
                        "customer_id": "CUST_001",
                        "tenure": 12,
                        "monthly_charges": 79.99,
                        "total_charges": 959.88,
                        "contract_type": "Month-to-month",
                        "payment_method": "Credit card",
                        "internet_service": "Fiber optic",
                        "phone_service": "Yes"
                    }
                ],
                "model_version": "v1.0",
                "return_probabilities": True
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""
    
    predictions: List[ChurnPredictionResponse] = Field(..., description="List of predictions")
    batch_id: str = Field(..., description="Batch identifier")
    processed_count: int = Field(..., description="Number of processed customers")
    error_count: int = Field(..., description="Number of errors")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "customer_id": "CUST_001",
                        "churn_probability": 0.75,
                        "churn_prediction": True,
                        "risk_level": "high",
                        "model_version": "v1.0",
                        "prediction_time": "2023-01-01T00:00:00Z",
                        "feature_importance": {}
                    }
                ],
                "batch_id": "batch_123456",
                "processed_count": 1,
                "error_count": 0,
                "processing_time": 2.5
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Pipeline not found",
                "error_code": "PIPELINE_NOT_FOUND",
                "timestamp": "2023-01-01T00:00:00Z",
                "details": {"pipeline_name": "invalid_pipeline"}
            }
        }