from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from limits.storage import RedisStorage
from core.config import settings

# Initialize Redis storage for limits
storage = RedisStorage(settings.redis_url)

# Create a Limiter object
# default_limits: lenient global limit for all routes
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=["100/minute"]
)
