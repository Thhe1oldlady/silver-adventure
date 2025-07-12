"""
Models module initialization.
"""

from app.models.schemas import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    BatchChurnPredictionRequest,
    BatchChurnPredictionResponse,
    JSONProcessingRequest,
    JSONProcessingResponse,
    OracleQueryRequest,
    OracleQueryResponse,
    OracleStatusResponse,
    DataUploadResponse,
    DataExportRequest,
    HealthResponse,
    ErrorResponse,
)

from app.models.database import (
    Customer,
    ChurnPrediction,
    ProcessingJob,
    ApiLog,
)

__all__ = [
    # Schemas
    "ChurnPredictionRequest",
    "ChurnPredictionResponse", 
    "BatchChurnPredictionRequest",
    "BatchChurnPredictionResponse",
    "JSONProcessingRequest",
    "JSONProcessingResponse",
    "OracleQueryRequest",
    "OracleQueryResponse",
    "OracleStatusResponse",
    "DataUploadResponse",
    "DataExportRequest",
    "HealthResponse",
    "ErrorResponse",
    # Database models
    "Customer",
    "ChurnPrediction",
    "ProcessingJob",
    "ApiLog",
]