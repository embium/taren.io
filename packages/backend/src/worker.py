import logging
from arq.connections import RedisSettings
from core.config import settings
from services.reddit_service import run_reddit_job

logger = logging.getLogger(__name__)

async def startup(ctx):
    logger.info("Starting ARQ Worker...")

async def shutdown(ctx):
    logger.info("Shutting down ARQ Worker...")

class WorkerSettings:
    """Settings for the ARQ worker."""
    functions = [run_reddit_job]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 3600  # 1 hour max job time
