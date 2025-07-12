"""
Health check endpoints.
"""

from fastapi import APIRouter, Request
from app.models.schemas import HealthResponse
from app.core.logging import get_logger
import time

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint.
    """
    app_state = request.app.state
    
    # Check service health
    services_health = {
        "ml_service": hasattr(app_state, 'ml_service') and app_state.ml_service.is_initialized,
        "oracle_service": hasattr(app_state, 'oracle_service') and app_state.oracle_service.is_initialized,
    }
    
    overall_health = "healthy" if all(services_health.values()) else "degraded"
    
    return HealthResponse(
        status=overall_health,
        app_name="Oracle FastAPI Integration",
        version="1.0.0",
        timestamp=time.time()
    )


@router.get("/detailed")
async def detailed_health_check(request: Request):
    """
    Detailed health check endpoint.
    """
    app_state = request.app.state
    
    # Check ML service
    ml_health = {
        "initialized": hasattr(app_state, 'ml_service') and app_state.ml_service.is_initialized,
        "model_loaded": False,
        "service_type": "machine_learning"
    }
    
    if hasattr(app_state, 'ml_service') and app_state.ml_service.is_initialized:
        ml_info = await app_state.ml_service.get_model_info()
        ml_health.update(ml_info)
        ml_health["model_loaded"] = ml_info.get("initialized", False)
    
    # Check Oracle service
    oracle_health = {
        "initialized": hasattr(app_state, 'oracle_service') and app_state.oracle_service.is_initialized,
        "connected": False,
        "service_type": "database"
    }
    
    if hasattr(app_state, 'oracle_service') and app_state.oracle_service.is_initialized:
        oracle_status = await app_state.oracle_service.get_status()
        oracle_health.update(oracle_status.dict())
    
    # Overall status
    services_healthy = ml_health["initialized"] and oracle_health["initialized"]
    overall_status = "healthy" if services_healthy else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "services": {
            "ml_service": ml_health,
            "oracle_service": oracle_health
        }
    }