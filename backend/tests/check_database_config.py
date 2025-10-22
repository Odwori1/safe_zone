#!/usr/bin/env python3
"""
CHECK DATABASE CONFIGURATION - FIXED
"""
import os
import asyncio
from app.core.config import settings

def check_database_config():
    """Check current database configuration"""
    print("🔧 DATABASE CONFIGURATION CHECK")
    print("=" * 50)
    
    # Check environment variables
    env_vars = [
        'DATABASE_URL',
        'DATABASE_HOST', 
        'DATABASE_PORT',
        'DATABASE_NAME',
        'DATABASE_USER',
        'DATABASE_PASSWORD'
    ]
    
    print("📋 ENVIRONMENT VARIABLES:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask password for security
            if 'PASSWORD' in var:
                masked = value[:3] + '***' if len(value) > 3 else '***'
                print(f"  {var}: {masked}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: ❌ NOT SET")
    
    print("\n📋 SETTINGS OBJECT:")
    try:
        attrs = [attr for attr in dir(settings) if not attr.startswith('_')]
        for attr in attrs:
            if 'DATABASE' in attr or 'DB' in attr:
                value = getattr(settings, attr)
                if value and 'PASSWORD' in attr:
                    masked = value[:3] + '***' if len(value) > 3 else '***'
                    print(f"  {attr}: {masked}")
                else:
                    print(f"  {attr}: {value}")
    except Exception as e:
        print(f"Error reading settings: {e}")

async def test_database_connection():
    """Test database connection with current config"""
    print("\n🔌 TESTING DATABASE CONNECTION:")
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME
        )
        print("✅ DATABASE CONNECTION SUCCESSFUL")
        
        # Check current user
        user_info = await conn.fetchrow("SELECT current_user, version()")
        print(f"  Connected as: {user_info['current_user']}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ DATABASE CONNECTION FAILED: {e}")
        return False

if __name__ == "__main__":
    check_database_config()
    
    # Test connection
    asyncio.run(test_database_connection())
