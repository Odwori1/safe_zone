import asyncpg
import logging
from app.utils.timezone import timezone_handler  # NEW

# Create module-specific logger to avoid circular imports
logger = logging.getLogger("safe_zone.database")

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool = None

    async def connect(self):
        try:
            # Import settings here to avoid circular imports
            from app.core.config import settings

            logger.info(f"Attempting to connect to: {settings.db_host}:{settings.db_port}/{settings.db_name}")

            self.pool = await asyncpg.create_pool(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                database=settings.db_name,
                min_size=1,
                max_size=10,
                command_timeout=60,
                # Timezone configuration (initial setup)
                server_settings={
                    'timezone': 'UTC',
                }
            )
            logger.info("Database connection pool created successfully")
            
            # TIMEZONE CONFIGURATION - VERIFY AND ADJUST
            await self._verify_timezone()

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            from app.core.config import settings
            logger.error(f"Connection details - Host: {settings.db_host}, Port: {settings.db_port}, DB: {settings.db_name}, User: {settings.db_user}")
            raise

    async def _verify_timezone(self):
        """Verify and configure timezone settings - ESSENTIAL for global app"""
        async with self.pool.acquire() as connection:
            # Ensure UTC timezone
            await connection.execute("SET TIME ZONE 'UTC';")
            
            # Verify timezone
            db_timezone = await connection.fetchval("SHOW timezone;")
            current_time = await connection.fetchval("SELECT NOW();")
            
            logger.info(f"Database timezone configured: {db_timezone}")
            logger.info(f"Current database time (UTC): {current_time}")
            
            # Test timezone-aware timestamp
            test_timestamp = await connection.fetchval("SELECT NOW()::timestamptz;")
            logger.info(f"Timezone-aware timestamp: {test_timestamp}")

            # Verify we can handle timezone conversions
            timezone_test = await connection.fetchval("""
                SELECT (NOW() AT TIME ZONE 'UTC') = (NOW() AT TIME ZONE 'US/Eastern' AT TIME ZONE 'UTC');
            """)
            logger.info(f"Timezone conversion test passed: {timezone_test}")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def execute(self, query: str, *args, user_id: str = None):
        async with self.pool.acquire() as connection:
            if user_id:
                await connection.execute("SELECT set_current_user_id($1);", user_id)
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args, user_id: str = None):
        async with self.pool.acquire() as connection:
            if user_id:
                await connection.execute("SELECT set_current_user_id($1);", user_id)
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args, user_id: str = None):
        async with self.pool.acquire() as connection:
            if user_id:
                await connection.execute("SELECT set_current_user_id($1);", user_id)
            return await connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args, user_id: str = None):
        async with self.pool.acquire() as connection:
            if user_id:
                await connection.execute("SELECT set_current_user_id($1);", user_id)
            return await connection.fetchval(query, *args)

# Global database instance
database = Database()

async def init_db():
    await database.connect()

async def close_db():
    await database.close()
