"""
Churn prediction endpoints.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import List
import time

from app.models.schemas import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    BatchChurnPredictionRequest,
    BatchChurnPredictionResponse
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/churn", response_model=ChurnPredictionResponse)
async def predict_churn(request: ChurnPredictionRequest, app_request: Request):
    """
    Predict churn for a single customer.
    """
    try:
        # Get ML service from app state
        ml_service = app_request.app.state.ml_service
        if not ml_service or not ml_service.is_initialized:
            raise HTTPException(status_code=503, detail="ML service not available")
        
        # Make prediction
        prediction = await ml_service.predict_churn(request)
        
        logger.info(f"Churn prediction completed for customer {request.customer_id}")
        return prediction
        
    except Exception as e:
        logger.error(f"Churn prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/churn/batch", response_model=BatchChurnPredictionResponse)
async def predict_churn_batch(request: BatchChurnPredictionRequest, app_request: Request):
    """
    Predict churn for multiple customers.
    """
    try:
        start_time = time.time()
        
        # Get ML service from app state
        ml_service = app_request.app.state.ml_service
        if not ml_service or not ml_service.is_initialized:
            raise HTTPException(status_code=503, detail="ML service not available")
        
        # Make predictions
        predictions = await ml_service.predict_batch(request.customers)
        
        processing_time = time.time() - start_time
        
        # Generate summary
        risk_levels = [p.risk_level for p in predictions]
        summary = {
            "total_customers": len(request.customers),
            "successful_predictions": len(predictions),
            "failed_predictions": len(request.customers) - len(predictions),
            "risk_distribution": {
                "low": risk_levels.count("low"),
                "medium": risk_levels.count("medium"),
                "high": risk_levels.count("high")
            },
            "average_churn_probability": sum(p.churn_probability for p in predictions) / len(predictions) if predictions else 0
        }
        
        logger.info(f"Batch churn prediction completed for {len(request.customers)} customers")
        
        return BatchChurnPredictionResponse(
            predictions=predictions,
            summary=summary,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Batch churn prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/churn/model-info")
async def get_model_info(app_request: Request):
    """
    Get ML model information.
    """
    try:
        # Get ML service from app state
        ml_service = app_request.app.state.ml_service
        if not ml_service or not ml_service.is_initialized:
            raise HTTPException(status_code=503, detail="ML service not available")
        
        model_info = await ml_service.get_model_info()
        return model_info
        
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/churn/feature-importance")
async def get_feature_importance(app_request: Request):
    """
    Get feature importance from the churn prediction model.
    """
    try:
        # Get ML service from app state
        ml_service = app_request.app.state.ml_service
        if not ml_service or not ml_service.is_initialized:
            raise HTTPException(status_code=503, detail="ML service not available")
        
        if not ml_service.model:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Get feature importance
        importance = ml_service.model.feature_importances_
        features = ml_service.feature_names
        
        feature_importance = [
            {"feature": feature, "importance": float(imp)}
            for feature, imp in zip(features, importance)
        ]
        
        # Sort by importance
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "feature_importance": feature_importance,
            "model_type": type(ml_service.model).__name__,
            "feature_count": len(features)
        }
        
    except Exception as e:
        logger.error(f"Failed to get feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))