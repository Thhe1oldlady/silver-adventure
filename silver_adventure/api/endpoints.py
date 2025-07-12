"""API endpoints for Silver Adventure."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import get_config
from ..core.logger import get_logger
from ..core.pipeline import Pipeline, PipelineContext
from ..ml.churn_prediction import ChurnPredictor
from ..pipeline.registry import PipelineRegistry
from .models import (
    PipelineRequest, PipelineResponse, PipelineStatus,
    ChurnPredictionRequest, ChurnPredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    HealthCheckResponse, MetricsResponse
)

router = APIRouter()
logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# Global instances
pipeline_registry = PipelineRegistry()
churn_predictor = ChurnPredictor()

# In-memory storage for async executions (in production, use Redis or database)
execution_store: Dict[str, Dict[str, Any]] = {}


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current authenticated user (placeholder for actual auth)."""
    # In production, implement proper JWT token validation
    return {"user_id": "anonymous"}


@router.post("/pipelines/execute", response_model=PipelineResponse)
async def execute_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Execute a pipeline."""
    execution_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    logger.info(f"Pipeline execution request: {request.pipeline_name}")
    
    try:
        # Get pipeline from registry
        pipeline = pipeline_registry.get_pipeline(request.pipeline_name)
        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail=f"Pipeline '{request.pipeline_name}' not found"
            )
        
        if request.async_execution:
            # Store execution info
            execution_store[execution_id] = {
                "pipeline_name": request.pipeline_name,
                "status": PipelineStatus.PENDING,
                "start_time": start_time,
                "end_time": None,
                "result": None,
                "errors": [],
                "metadata": {}
            }
            
            # Execute in background
            background_tasks.add_task(
                execute_pipeline_async,
                execution_id,
                pipeline,
                request.data,
                request.config
            )
            
            return PipelineResponse(
                pipeline_name=request.pipeline_name,
                execution_id=execution_id,
                status=PipelineStatus.PENDING,
                start_time=start_time,
                metadata={"async": True}
            )
        
        else:
            # Execute synchronously
            context = pipeline.execute(request.data, request.config)
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return PipelineResponse(
                pipeline_name=request.pipeline_name,
                execution_id=execution_id,
                status=PipelineStatus.COMPLETED if not context.has_errors() else PipelineStatus.FAILED,
                result=context.data,
                metadata=context.metadata,
                errors=[str(error) for error in context.errors],
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
    
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return PipelineResponse(
            pipeline_name=request.pipeline_name,
            execution_id=execution_id,
            status=PipelineStatus.FAILED,
            errors=[str(e)],
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )


@router.get("/pipelines/status/{execution_id}", response_model=PipelineResponse)
async def get_pipeline_status(execution_id: str):
    """Get pipeline execution status."""
    if execution_id not in execution_store:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found"
        )
    
    execution_info = execution_store[execution_id]
    
    duration = None
    if execution_info["end_time"]:
        duration = (execution_info["end_time"] - execution_info["start_time"]).total_seconds()
    
    return PipelineResponse(
        pipeline_name=execution_info["pipeline_name"],
        execution_id=execution_id,
        status=execution_info["status"],
        result=execution_info["result"],
        metadata=execution_info["metadata"],
        errors=execution_info["errors"],
        start_time=execution_info["start_time"],
        end_time=execution_info["end_time"],
        duration=duration
    )


@router.get("/pipelines/list")
async def list_pipelines():
    """List available pipelines."""
    return {
        "pipelines": pipeline_registry.list_pipelines(),
        "count": len(pipeline_registry.list_pipelines())
    }


@router.post("/ml/churn/predict", response_model=ChurnPredictionResponse)
async def predict_churn(
    request: ChurnPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Predict customer churn."""
    logger.info(f"Churn prediction request for customer: {request.customer_id}")
    
    try:
        # Make prediction
        prediction = churn_predictor.predict_single(
            request.features,
            model_version=request.model_version
        )
        
        # Determine risk level
        risk_level = "low"
        if prediction["churn_probability"] > 0.7:
            risk_level = "high"
        elif prediction["churn_probability"] > 0.4:
            risk_level = "medium"
        
        return ChurnPredictionResponse(
            customer_id=request.customer_id,
            churn_probability=prediction["churn_probability"],
            churn_prediction=prediction["churn_prediction"],
            risk_level=risk_level,
            model_version=prediction["model_version"],
            prediction_time=datetime.utcnow(),
            feature_importance=prediction.get("feature_importance", {})
        )
    
    except Exception as e:
        logger.error(f"Churn prediction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Churn prediction failed: {str(e)}"
        )


@router.post("/ml/churn/predict/batch", response_model=BatchPredictionResponse)
async def predict_churn_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Predict churn for multiple customers."""
    batch_id = str(uuid.uuid4())
    logger.info(f"Batch churn prediction request: {len(request.customers)} customers")
    
    try:
        # Make predictions
        predictions = churn_predictor.predict_batch(
            request.customers,
            model_version=request.model_version,
            return_probabilities=request.return_probabilities
        )
        
        # Convert to response format
        prediction_responses = []
        for customer, prediction in zip(request.customers, predictions):
            customer_id = customer.get("customer_id", "unknown")
            
            # Determine risk level
            risk_level = "low"
            if prediction["churn_probability"] > 0.7:
                risk_level = "high"
            elif prediction["churn_probability"] > 0.4:
                risk_level = "medium"
            
            prediction_responses.append(ChurnPredictionResponse(
                customer_id=customer_id,
                churn_probability=prediction["churn_probability"],
                churn_prediction=prediction["churn_prediction"],
                risk_level=risk_level,
                model_version=prediction["model_version"],
                prediction_time=datetime.utcnow(),
                feature_importance=prediction.get("feature_importance", {})
            ))
        
        return BatchPredictionResponse(
            predictions=prediction_responses,
            batch_id=batch_id,
            processed_count=len(prediction_responses),
            error_count=0,
            processing_time=0.0  # Calculate actual processing time
        )
    
    except Exception as e:
        logger.error(f"Batch churn prediction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch churn prediction failed: {str(e)}"
        )


@router.get("/ml/models/list")
async def list_models():
    """List available ML models."""
    return {
        "models": [
            {
                "name": "churn_predictor",
                "version": "v1.0",
                "type": "classification",
                "status": "active"
            }
        ]
    }


@router.get("/monitoring/health", response_model=HealthCheckResponse)
async def health_check_detailed():
    """Detailed health check."""
    # Check dependencies
    dependencies = {
        "database": "healthy",  # Would check actual database connection
        "cache": "healthy",     # Would check Redis connection
        "ml_service": "healthy" # Would check ML model availability
    }
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        uptime=0.0,  # Calculate actual uptime
        dependencies=dependencies
    )


@router.get("/monitoring/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get application metrics."""
    # In production, collect actual metrics
    metrics = {
        "pipeline_executions_total": 0,
        "pipeline_duration_avg": 0.0,
        "prediction_requests_total": 0,
        "prediction_accuracy": 0.0,
        "active_connections": 0,
        "memory_usage": 0.0,
        "cpu_usage": 0.0
    }
    
    return MetricsResponse(
        timestamp=datetime.utcnow(),
        metrics=metrics
    )


async def execute_pipeline_async(
    execution_id: str,
    pipeline: Pipeline,
    input_data: Any,
    config: Optional[Dict[str, Any]]
):
    """Execute pipeline asynchronously."""
    execution_store[execution_id]["status"] = PipelineStatus.RUNNING
    
    try:
        # Execute pipeline
        context = pipeline.execute(input_data, config)
        
        # Update execution info
        execution_store[execution_id].update({
            "status": PipelineStatus.COMPLETED if not context.has_errors() else PipelineStatus.FAILED,
            "result": context.data,
            "metadata": context.metadata,
            "errors": [str(error) for error in context.errors],
            "end_time": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Async pipeline execution failed: {str(e)}")
        execution_store[execution_id].update({
            "status": PipelineStatus.FAILED,
            "errors": [str(e)],
            "end_time": datetime.utcnow()
        })