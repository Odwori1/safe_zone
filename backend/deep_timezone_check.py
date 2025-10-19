#!/usr/bin/env python3
"""
Deep investigation of timezone configuration
"""

import asyncio
import asyncpg
from app.core.config import settings

async def deep_timezone_check():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("🔍 DEEP TIMEZONE INVESTIGATION")
        print("=" * 50)
        
        # 1. Check database-level timezone
        db_timezone = await conn.fetchval("SHOW timezone;")
        print(f"📊 Database timezone setting: {db_timezone}")
        
        # 2. Check server timezone
        server_timezone = await conn.fetchval("SELECT current_setting('TIMEZONE');")
        print(f"🖥️  Server timezone: {server_timezone}")
        
        # 3. Check session timezone
        session_timezone = await conn.fetchval("SELECT current_setting('TimeZone');")
        print(f"💻 Session timezone: {session_timezone}")
        
        # 4. Check actual time values
        print("\n🕐 TIME COMPARISONS:")
        now_utc = await conn.fetchval("SELECT NOW() AT TIME ZONE 'UTC';")
        now_local = await conn.fetchval("SELECT NOW();")
        now_with_tz = await conn.fetchval("SELECT CURRENT_TIMESTAMP;")
        
        print(f"NOW() AT TIME ZONE 'UTC': {now_utc}")
        print(f"NOW() (local): {now_local}")
        print(f"CURRENT_TIMESTAMP: {now_with_tz}")
        
        # 5. Check timezone offset
        timezone_offset = await conn.fetchval("SELECT EXTRACT(TIMEZONE_HOUR FROM NOW());")
        print(f"⏰ Timezone offset (hours): {timezone_offset}")
        
        # 6. Check if timestamptz is working correctly
        timestamptz_test = await conn.fetchval("SELECT pg_typeof(NOW());")
        print(f"📝 NOW() data type: {timestamptz_test}")
        
        # 7. Test timezone conversion
        print("\n🔄 TIMEZONE CONVERSION TESTS:")
        test1 = await conn.fetchval("""
            SELECT (NOW() AT TIME ZONE 'UTC') = (NOW() AT TIME ZONE 'UTC');
        """)
        print(f"UTC to UTC comparison: {test1}")
        
        test2 = await conn.fetchval("""
            SELECT (NOW() AT TIME ZONE 'UTC') = (NOW() AT TIME ZONE 'Asia/Dubai' AT TIME ZONE 'UTC');
        """)
        print(f"UTC vs Asia/Dubai->UTC: {test2}")
        
        test3 = await conn.fetchval("""
            SELECT EXTRACT(TIMEZONE FROM NOW()) = 14400;
        """)
        print(f"Asia/Dubai offset (14400 seconds): {test3}")
        
        # 8. Check database configuration
        print("\n⚙️ DATABASE CONFIGURATION:")
        timezone_config = await conn.fetch("""
            SELECT name, setting, unit, context 
            FROM pg_settings 
            WHERE name LIKE '%timezone%' OR name = 'log_timezone';
        """)
        
        for config in timezone_config:
            print(f"{config['name']}: {config['setting']} ({config['context']})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(deep_timezone_check())
