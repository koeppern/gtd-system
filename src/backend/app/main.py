"""
Main FastAPI application for GTD backend
"""
import logging
import sys
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import get_settings
from app.database import test_connection
from app.api import users, fields, projects, tasks, dashboard, search, quick_add

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting GTD Backend Application")
    settings = get_settings()
    logger.info(f"Environment: {settings.app.environment}")
    
    # Test Supabase connection
    try:
        if test_connection():
            logger.info("Supabase connection successful")
        else:
            logger.warning("Supabase connection test failed - some features may not work")
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        logger.warning("Starting server without database connection - some features may not work")
        # Don't raise in development to allow server to start without DB
    
    yield
    
    # Shutdown
    logger.info("Shutting down GTD Backend Application")


# Create FastAPI application
def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app.name,
        description="GTD (Getting Things Done) System Backend API",
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.app.debug else None,
        redoc_url="/redoc" if settings.app.debug else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    
    # Include API routers
    app.include_router(users.router, prefix="/api")
    app.include_router(fields.router, prefix="/api")
    app.include_router(projects.router, prefix="/api")
    app.include_router(tasks.router, prefix="/api")
    app.include_router(dashboard.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(quick_add.router, prefix="/api")
    
    return app


# Create app instance
app = create_app()


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors
    """
    logger.warning(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )




@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    logger.error(f"Unexpected error for {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Health status
    """
    settings = get_settings()
    
    # Test database connection
    db_status = "healthy"
    try:
        from app.database import test_connection
        if not test_connection():
            db_status = "unhealthy: Supabase connection failed"
    except Exception as e:
        db_status = f"unhealthy: {e}"
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "app": {
            "name": settings.app.name,
            "version": settings.app.version,
            "environment": settings.app.environment
        },
        "database": {
            "status": db_status
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    
    Returns:
        dict: API information
    """
    settings = get_settings()
    return {
        "message": "GTD Backend API",
        "version": settings.app.version,
        "docs_url": "/docs" if settings.app.debug else None,
        "health_url": "/health"
    }


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url} - Started")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        access_log=True
    )