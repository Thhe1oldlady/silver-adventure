"""
Pydantic models for API requests and responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    """
    Status enumeration.
    """
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"


class HealthResponse(BaseModel):
    """
    Health check response model.
    """
    status: str
    app_name: str
    version: str
    timestamp: float


class ErrorResponse(BaseModel):
    """
    Error response model.
    """
    message: str
    detail: Optional[str] = None
    status: StatusEnum = StatusEnum.ERROR


class ChurnPredictionRequest(BaseModel):
    """
    Churn prediction request model.
    """
    customer_id: str = Field(..., description="Customer identifier")
    features: Dict[str, Any] = Field(..., description="Customer features for prediction")
    
    @validator('features')
    def validate_features(cls, v):
        """
        Validate features dictionary.
        """
        required_fields = ['age', 'tenure', 'monthly_charges', 'total_charges']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v


class ChurnPredictionResponse(BaseModel):
    """
    Churn prediction response model.
    """
    customer_id: str
    churn_probability: float = Field(..., ge=0, le=1, description="Probability of churn (0-1)")
    risk_level: str = Field(..., description="Risk level (low, medium, high)")
    factors: List[str] = Field(default_factory=list, description="Key factors influencing prediction")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        """
        Validate risk level.
        """
        valid_levels = ['low', 'medium', 'high']
        if v not in valid_levels:
            raise ValueError(f"Risk level must be one of: {valid_levels}")
        return v


class BatchChurnPredictionRequest(BaseModel):
    """
    Batch churn prediction request model.
    """
    customers: List[ChurnPredictionRequest] = Field(..., description="List of customers for prediction")
    
    @validator('customers')
    def validate_customers(cls, v):
        """
        Validate customers list.
        """
        if not v:
            raise ValueError("Customers list cannot be empty")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 customers per batch")
        return v


class BatchChurnPredictionResponse(BaseModel):
    """
    Batch churn prediction response model.
    """
    predictions: List[ChurnPredictionResponse] = Field(..., description="List of predictions")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    processing_time: float = Field(..., description="Processing time in seconds")


class JSONProcessingRequest(BaseModel):
    """
    JSON processing request model.
    """
    data: Dict[str, Any] = Field(..., description="JSON data to process")
    script_name: Optional[str] = Field(None, description="Name of processing script to use")
    options: Dict[str, Any] = Field(default_factory=dict, description="Processing options")


class JSONProcessingResponse(BaseModel):
    """
    JSON processing response model.
    """
    processed_data: Dict[str, Any] = Field(..., description="Processed JSON data")
    script_used: str = Field(..., description="Name of script used for processing")
    processing_time: float = Field(..., description="Processing time in seconds")
    status: StatusEnum = StatusEnum.SUCCESS


class OracleQueryRequest(BaseModel):
    """
    Oracle query request model.
    """
    query: str = Field(..., description="SQL query to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    fetch_size: int = Field(default=100, ge=1, le=10000, description="Maximum number of rows to fetch")


class OracleQueryResponse(BaseModel):
    """
    Oracle query response model.
    """
    data: List[Dict[str, Any]] = Field(..., description="Query results")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time: float = Field(..., description="Query execution time in seconds")
    columns: List[str] = Field(..., description="Column names")


class OracleStatusResponse(BaseModel):
    """
    Oracle database status response model.
    """
    connected: bool = Field(..., description="Connection status")
    version: Optional[str] = Field(None, description="Oracle database version")
    service_name: Optional[str] = Field(None, description="Service name")
    connection_pool_size: int = Field(..., description="Connection pool size")
    active_connections: int = Field(..., description="Active connections")


class DataUploadResponse(BaseModel):
    """
    Data upload response model.
    """
    file_id: str = Field(..., description="Unique identifier for uploaded file")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: datetime = Field(default_factory=datetime.now)
    status: StatusEnum = StatusEnum.SUCCESS


class DataExportRequest(BaseModel):
    """
    Data export request model.
    """
    table_name: str = Field(..., description="Name of table to export")
    format: str = Field(default="json", description="Export format (json, csv, xlsx)")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Export filters")
    
    @validator('format')
    def validate_format(cls, v):
        """
        Validate export format.
        """
        valid_formats = ['json', 'csv', 'xlsx']
        if v not in valid_formats:
            raise ValueError(f"Format must be one of: {valid_formats}")
        return v