from fastapi import Request
import logging

logger = logging.getLogger("safe_zone.rate_limiting")

async def rate_limit_middleware(request: Request, call_next):
    # DEVELOPMENT: Skip all rate limiting
    logger.debug("Rate limiting disabled for development")
    return await call_next(request)
