#!/usr/bin/env python3
"""
Check and fix timezone configuration
"""

import asyncio
import asyncpg
from app.core.config import settings

async def check_timezone():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        # Check current timezone
        timezone = await conn.fetchval("SHOW timezone;")
        print(f"📊 Database timezone: {timezone}")
        
        # Check timezone conversion
        conversion_test = await conn.fetchval("""
            SELECT (NOW() AT TIME ZONE 'UTC') = (NOW() AT TIME ZONE 'US/Eastern' AT TIME ZONE 'UTC');
        """)
        print(f"🕐 Timezone conversion test result: {conversion_test}")
        
        # Show current times in different formats
        current_utc = await conn.fetchval("SELECT NOW() AT TIME ZONE 'UTC';")
        current_local = await conn.fetchval("SELECT NOW();")
        print(f"🕐 Current time (UTC): {current_utc}")
        print(f"🕐 Current time (local): {current_local}")
        
        # This should return True for proper timezone handling
        proper_test = await conn.fetchval("""
            SELECT EXTRACT(TIMEZONE_HOUR FROM NOW()) = 0;
        """)
        print(f"🔧 UTC timezone check: {proper_test}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_timezone())
