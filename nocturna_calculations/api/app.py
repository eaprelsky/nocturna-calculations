"""
Main FastAPI application module
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram
import time
import uuid

from nocturna_calculations.api.config import settings
from nocturna_calculations.api.routers import auth, charts, calculations, websocket

# Create FastAPI app
app = FastAPI(
    title="Nocturna Calculations API",
    description="Astrological calculations API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

# Middleware for request ID and metrics
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    return response

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
app.include_router(calculations.router, prefix="/api/calculations", tags=["Calculations"])
app.include_router(websocket.router, prefix="/api/websockets", tags=["WebSockets"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Nocturna Calculations API",
        "version": "1.0.0",
        "description": "Astrological calculations REST API",
        "status": "running",
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api": "/api"
        },
        "links": {
            "docs": "/docs",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Nocturna Calculations API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/api/auth",
            "charts": "/api/charts",
            "calculations": "/api/calculations",
            "websockets": "/api/websockets"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "details": None
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", None)
            }
        }
    ) 