import logging
from arq import create_pool
from arq.connections import RedisSettings
from core.config import settings

logger = logging.getLogger(__name__)

# Global redis pool for ARQ
redis_pool = None

async def init_redis_pool():
    global redis_pool
    logger.info(f"Initializing ARQ Redis pool at {settings.redis_url}")
    redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))

async def close_redis_pool():
    global redis_pool
    if redis_pool:
        logger.info("Closing ARQ Redis pool")
        await redis_pool.close()
        redis_pool = None

def get_redis_pool():
    if not redis_pool:
        raise RuntimeError("Redis pool not initialized")
    return redis_pool
