"""FastAPI server setup and configuration."""

import time
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from starlette.responses import Response

from ..core.config import get_config
from ..core.logger import get_logger
from .endpoints import router
from .models import ErrorResponse

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_config()
    
    # Create FastAPI app
    app = FastAPI(
        title="Silver Adventure API",
        description="PyPy-optimized pipeline system for data processing and AI integration",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        
        # Track request
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Track duration
            REQUEST_DURATION.observe(process_time)
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        error_response = ErrorResponse(
            error=str(exc),
            error_code="INTERNAL_SERVER_ERROR",
            timestamp=datetime.utcnow()
        )
        return JSONResponse(
            status_code=500,
            content=error_response.dict()
        )
    
    # Add HTTP exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_response = ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow()
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict()
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "0.1.0",
            "uptime": time.time() - app.state.start_time
        }
    
    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    # Add routers
    app.include_router(router, prefix="/api/v1")
    
    # Store app start time
    app.state.start_time = time.time()
    
    return app


def run_server():
    """Run the FastAPI server."""
    config = get_config()
    
    logger.info(f"Starting Silver Adventure API server on {config.api.host}:{config.api.port}")
    
    uvicorn.run(
        "silver_adventure.api.server:create_app",
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug,
        reload=config.api.reload,
        workers=config.api.workers,
        factory=True
    )


# Create app instance
app = create_app()