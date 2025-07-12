"""
Main FastAPI application module.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import engine, SessionLocal
from app.services.ml_service import MLService
from app.services.oracle_service import OracleService

logger = get_logger(__name__)

# Global services
ml_service = None
oracle_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.
    """
    global ml_service, oracle_service
    
    logger.info("Starting application...")
    
    # Initialize services
    try:
        ml_service = MLService()
        await ml_service.initialize()
        logger.info("ML service initialized successfully")
        
        oracle_service = OracleService()
        await oracle_service.initialize()
        logger.info("Oracle service initialized successfully")
        
        # Store services in app state
        app.state.ml_service = ml_service
        app.state.oracle_service = oracle_service
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")
    
    if oracle_service:
        await oracle_service.close()
    
    if ml_service:
        await ml_service.close()
    
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Oracle Tech Integration with FastAPI and Churn Prediction",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add processing time header to responses.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests and responses.
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host,
        }
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
        }
    )
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    """
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "exception": str(exc),
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Oracle FastAPI Integration",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )