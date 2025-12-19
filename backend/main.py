"""Main application entry point for the Ariadne backend."""

import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.registry import registry
from api.v1.research.router import router as research_router
from api.v1.users.router import router as users_router
from api.v1.tapestries.router import router as tapestries_router
from auth.jwt_middleware import JWTMiddleware
from auth.rate_limiter import RateLimitMiddleware
from services.user_service import UserService
from services.muse_service import MuseService
from services.tapestry_service import TapestryService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Ariadne backend...")
    
    # Discover and register all plugins
    logger.info("Discovering plugins...")
    registry.discover_plugins('plugins.tools')
    registry.discover_plugins('plugins.learning_models')
    
    # Initialize services
    logger.info("Initializing services...")
    user_service = UserService()
    muse_service = MuseService()
    tapestry_service = TapestryService()
    
    # Store services in app state for dependency injection
    app.state.user_service = user_service
    app.state.muse_service = muse_service
    app.state.tapestry_service = tapestry_service
    
    logger.info("Ariadne backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ariadne backend...")
    # Cleanup resources here if needed


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ariadne - Your AI Research Partner",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)

# Add middleware
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Trusted host middleware (security)
if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["ariadne.ai", "*.ariadne.ai", "localhost"]
    )

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# JWT authentication middleware
app.add_middleware(JWTMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if settings.is_production else str(exc)
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.is_development else None
    }


# API v1 routers
app.include_router(research_router, prefix="/api/v1/research", tags=["research"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(tapestries_router, prefix="/api/v1/tapestries", tags=["tapestries"])


def signal_handler(signum, frame):
    """Signal handler for graceful shutdown."""
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.monitoring.log_level.lower(),
        access_log=True
    )
