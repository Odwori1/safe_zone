"""
Redis Service for Real-time Messaging - Phase 3, Item 4
Following security-first blueprint with Redis Pub/Sub
"""
import logging
import json
import asyncio
from typing import Optional, Callable, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger("safe_zone.redis_service")

class RedisService:
    """
    Redis service for real-time message delivery
    Enables cross-instance WebSocket communication
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.PubSub] = None
        self.is_connected = False

    async def connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host if hasattr(settings, 'redis_host') else 'localhost',
                port=settings.redis_port if hasattr(settings, 'redis_port') else 6379,
                password=settings.redis_password if hasattr(settings, 'redis_password') else None,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.is_connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Redis connection closed")

    async def publish_message(self, channel: str, message: dict) -> bool:
        """
        Publish message to Redis channel
        Used for cross-instance message delivery
        """
        if not self.is_connected or not self.redis_client:
            logger.warning("Redis not connected, message not published")
            return False

        try:
            await self.redis_client.publish(channel, json.dumps(message))
            logger.debug(f"Message published to channel: {channel}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to {channel}: {e}")
            return False

    async def subscribe_to_channel(self, channel: str, message_handler: Callable):
        """
        Subscribe to Redis channel and handle messages
        """
        if not self.is_connected or not self.redis_client:
            logger.warning("Redis not connected, cannot subscribe")
            return

        try:
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(channel)
            logger.info(f"Subscribed to Redis channel: {channel}")

            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        message_data = json.loads(message['data'])
                        await message_handler(message_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Redis message: {e}")

        except Exception as e:
            logger.error(f"Redis subscription error for {channel}: {e}")
        finally:
            if self.pubsub:
                await self.pubsub.unsubscribe(channel)
                await self.pubsub.close()

# Global Redis service instance
redis_service = RedisService()
