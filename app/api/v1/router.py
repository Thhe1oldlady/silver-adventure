"""
API v1 router.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, churn, oracle, data

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(churn.router, prefix="/predict", tags=["churn-prediction"])
api_router.include_router(oracle.router, prefix="/oracle", tags=["oracle"])
api_router.include_router(data.router, prefix="/data", tags=["data-management"])