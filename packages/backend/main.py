"""FastAPI application entry point for DDD Authentication System."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.error_handlers import register_error_handlers
from api.routers import auth, users
from config.settings import settings
from infrastructure.database.connection import async_engine
from infrastructure.database.models import Base
from infrastructure.events.event_bus import get_event_bus
from infrastructure.events.event_handlers import register_event_handlers

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

    # Register event handlers with email service
    from api.dependencies import get_email_service

    event_bus = get_event_bus()
    email_service = get_email_service()
    register_event_handlers(event_bus, email_service)
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)

# Register settings router for email management
from api.routers import settings

app.include_router(settings.router)

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
