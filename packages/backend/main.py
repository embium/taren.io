"""FastAPI application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import async_engine, settings
from core.database import Base
from routers import auth, users, stripe as stripe_router
from routers import reddit as reddit_router
from services.email_service import EmailService
from core.queue import init_redis_pool, close_redis_pool
import models.reddit  # noqa: F401 — registers reddit tables with Base.metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# async def run_forever():
#     while True:
#         print("Running...")
#         await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup: Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await init_redis_pool()
    logger.info("Application started successfully")

    yield

    # Shutdown: Close database connections
    await close_redis_pool()
    await async_engine.dispose()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Taren Authentication API",
    description="Simple and powerful authentication system",
    version="2.0.0",
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
app.include_router(reddit_router.router)
app.include_router(stripe_router.router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Taren API",
        "version": "2.0.0",
        "architecture": "3-layer",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
