import logging
import sys
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def setup_logging():
    # Import settings here to avoid circular imports
    from app.core.config import settings
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/safe_zone.log")
        ]
    )
    
    logger = logging.getLogger("safe_zone")
    logger.info("Logging setup completed")
    return logger

# Create logger instance
logger = setup_logging()
