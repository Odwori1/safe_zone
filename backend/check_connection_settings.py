#!/usr/bin/env python3
"""
Check database connection settings
"""

import asyncio
from app.database.database import database

async def check_connection_settings():
    try:
        print("🔧 CHECKING DATABASE CONNECTION SETTINGS")
        print("=" * 50)
        
        # Initialize database connection
        await database.connect()
        
        # Check connection settings
        async with database.pool.acquire() as conn:
            # Check what timezone this connection is using
            timezone = await conn.fetchval("SHOW timezone;")
            print(f"📊 Connection timezone: {timezone}")
            
            # Check if our timezone setting was applied
            applied_settings = await conn.fetchval("""
                SELECT current_setting('timezone') as tz;
            """)
            print(f"🔄 Applied timezone: {applied_settings}")
            
            # Test if we can change timezone for this session
            await conn.execute("SET TIME ZONE 'UTC';")
            new_timezone = await conn.fetchval("SHOW timezone;")
            print(f"🔄 New session timezone: {new_timezone}")
            
            # Test timestamps
            utc_time = await conn.fetchval("SELECT NOW() AT TIME ZONE 'UTC';")
            local_time = await conn.fetchval("SELECT NOW();")
            print(f"🕐 UTC time: {utc_time}")
            print(f"🕐 Local time: {local_time}")
            
        await database.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_connection_settings())
