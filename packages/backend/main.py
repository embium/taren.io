"""FastAPI application entry point for DDD Authentication System."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.error_handlers import register_error_handlers
from src.api.routers import auth, users
from src.config.settings import settings
from src.infrastructure.database.connection import async_engine
from src.infrastructure.database.models import Base
from src.infrastructure.events.event_bus import get_event_bus
from src.infrastructure.events.event_handlers import register_event_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup: Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Register event handlers
    event_bus = get_event_bus()
    register_event_handlers(event_bus)
    logger.info("Application started successfully")

    yield

    # Shutdown: Close database connections
    await async_engine.dispose()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Taren Authentication API",
    description="Enterprise-grade authentication system built with Domain-Driven Design",
    version="1.0.0",
    lifespan=lifespan,
)


# Add custom middleware for iOS Safari compatibility
@app.middleware("http")
async def add_cors_headers(request, call_next):
    """Add additional CORS headers for iOS Safari compatibility."""
    response = await call_next(request)

    # iOS Safari needs explicit Vary header for proper CORS caching
    response.headers["Vary"] = "Origin"

    # Add explicit CORS headers for preflight responses
    if request.method == "OPTIONS":
        response.headers["Access-Control-Max-Age"] = "3600"

    return response


# Configure CORS
# iOS Safari requires more explicit CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)

# Register error handlers
register_error_handlers(app)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Taren Authentication API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
