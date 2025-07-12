"""
Silver Adventure - Main FastAPI Application

This is the main entry point for the Silver Adventure application.
It includes FastAPI endpoints for health checks, churn prediction,
and email generation services.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
from datetime import datetime

from .services.email_service import EmailService
from .services.churn_service import ChurnService
from .utils.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Silver Adventure API",
    description="A comprehensive API with ML capabilities and email generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
email_service = EmailService()
churn_service = ChurnService()


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str


class EmailRequest(BaseModel):
    to_email: str
    template: str
    subject: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChurnPredictionRequest(BaseModel):
    customer_id: str
    features: Dict[str, float]


class ChurnPredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: str
    recommendations: list


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns basic health information"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Perform basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
        
        # Check services
        email_healthy = email_service.health_check()
        churn_healthy = churn_service.health_check()
        
        if not email_healthy or not churn_healthy:
            health_status["status"] = "degraded"
            
        return HealthResponse(**health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/api/v1/email/send")
async def send_email(request: EmailRequest):
    """Send a golden mood email"""
    try:
        result = await email_service.send_golden_mood_email(
            to_email=request.to_email,
            template=request.template,
            subject=request.subject,
            context=request.context or {}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Email sent successfully",
                "email_id": result.get("email_id"),
                "status": "sent"
            }
        )
        
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )


@app.get("/api/v1/email/templates")
async def get_email_templates():
    """Get available email templates"""
    try:
        templates = email_service.get_available_templates()
        return JSONResponse(
            status_code=200,
            content={"templates": templates}
        )
        
    except Exception as e:
        logger.error(f"Failed to get templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get templates: {str(e)}"
        )


@app.post("/api/v1/predict/churn", response_model=ChurnPredictionResponse)
async def predict_churn(request: ChurnPredictionRequest):
    """Predict customer churn probability"""
    try:
        prediction = await churn_service.predict_churn(
            customer_id=request.customer_id,
            features=request.features
        )
        
        return ChurnPredictionResponse(**prediction)
        
    except Exception as e:
        logger.error(f"Churn prediction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Churn prediction failed: {str(e)}"
        )


@app.get("/api/v1/predict/churn/features")
async def get_churn_features():
    """Get required features for churn prediction"""
    try:
        features = churn_service.get_required_features()
        return JSONResponse(
            status_code=200,
            content={"features": features}
        )
        
    except Exception as e:
        logger.error(f"Failed to get features: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get features: {str(e)}"
        )


@app.post("/api/v1/pipeline/train")
async def train_model():
    """Train or retrain the churn prediction model"""
    try:
        result = await churn_service.train_model()
        return JSONResponse(
            status_code=200,
            content={
                "message": "Model training completed",
                "model_id": result.get("model_id"),
                "accuracy": result.get("accuracy"),
                "status": "trained"
            }
        )
        
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Model training failed: {str(e)}"
        )


@app.get("/api/v1/pipeline/status")
async def get_pipeline_status():
    """Get the current pipeline status"""
    try:
        status = churn_service.get_pipeline_status()
        return JSONResponse(
            status_code=200,
            content=status
        )
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline status: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )