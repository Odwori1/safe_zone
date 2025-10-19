from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import time
import asyncio
import logging

# Create module-specific logger
logger = logging.getLogger("safe_zone.rate_limiting")

# Simple in-memory rate limiting (replace with Redis in production)
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    async def check_rate_limit(self, request: Request, identifier: str = None):
        # Import settings here to avoid circular imports
        from app.core.config import settings
        
        if settings.environment == "test":
            return True
            
        now = time.time()
        client_ip = request.client.host
        key = identifier or client_ip
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove requests outside the window (1 minute)
        window_start = now - 60
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if under limit
        if len(self.requests[key]) >= settings.rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded for {key}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again in a minute."
                }
            )
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

# Rate limiting middleware
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for docs and health endpoints
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/api/v1/health"]:
        return await call_next(request)
    
    try:
        await rate_limiter.check_rate_limit(request)
        response = await call_next(request)
        
        # Add rate limit headers
        from app.core.config import settings
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
        return response
        
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content=e.detail,
            headers={
                "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
