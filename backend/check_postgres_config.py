#!/usr/bin/env python3
"""
Check PostgreSQL server configuration
"""

import asyncio
import asyncpg
from app.core.config import settings

async def check_postgres_config():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("⚙️ POSTGRESQL SERVER CONFIGURATION")
        print("=" * 50)
        
        # Get all timezone-related settings
        settings_query = """
            SELECT name, setting, unit, context, vartype, source, sourcefile, sourceline
            FROM pg_settings 
            WHERE name IN ('timezone', 'log_timezone', 'TimeZone')
            OR name LIKE '%timezone%'
            ORDER BY name;
        """
        
        configs = await conn.fetch(settings_query)
        
        for config in configs:
            print(f"\n🔧 {config['name']}:")
            print(f"   Value: {config['setting']}")
            print(f"   Unit: {config['unit']}")
            print(f"   Context: {config['context']}")
            print(f"   Type: {config['vartype']}")
            print(f"   Source: {config['source']}")
            if config['sourcefile']:
                print(f"   Config file: {config['sourcefile']}:{config['sourceline']}")
        
        # Check if we're using Docker and what the container timezone is
        print(f"\n🐳 Checking Docker/container info...")
        try:
            # This will only work if we're in a Docker container
            with open('/etc/timezone', 'r') as f:
                container_tz = f.read().strip()
                print(f"Container timezone: {container_tz}")
        except:
            print("Not running in Docker container or /etc/timezone not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_postgres_config())
