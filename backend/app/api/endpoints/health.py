from fastapi import APIRouter
import logging

# Create module-specific logger
logger = logging.getLogger("safe_zone.health")

router = APIRouter()

@router.get("/health")
async def health_check():
    # Import here to avoid circular imports
    from app.database.database import database
    
    # Test database connection
    try:
        db_version = await database.fetchval("SELECT version()")
        logger.info("Health check - Database connected")
        return {
            "status": "healthy",
            "service": "Safe Zone API",
            "database": "connected",
            "database_version": db_version.split(",")[0],
            "environment": "development"
        }
    except Exception as e:
        logger.error(f"Health check - Database disconnected: {e}")
        return {
            "status": "unhealthy",
            "service": "Safe Zone API", 
            "database": "disconnected",
            "error": str(e),
            "environment": "development"
        }
