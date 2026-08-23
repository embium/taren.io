import logging
from arq.connections import RedisSettings
from core.config import settings
from services.reddit_service import run_reddit_job
from services.agent_service import run_agent_search_task

logger = logging.getLogger(__name__)


async def startup(ctx):
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting ARQ Worker...")


async def shutdown(ctx):
    logger.info("Shutting down ARQ Worker...")


class WorkerSettings:
    """Settings for the ARQ worker."""

    functions = [run_reddit_job, run_agent_search_task]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 3600  # 1 hour max job time
