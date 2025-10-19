import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv('.env')

async def test_connection():
    try:
        print("Testing database connection...")
        print(f"Host: {os.getenv('DB_HOST')}")
        print(f"Port: {os.getenv('DB_PORT')}")
        print(f"User: {os.getenv('DB_USER')}")
        print(f"DB: {os.getenv('DB_NAME')}")
        
        # Test with connection parameters
        conn = await asyncpg.connect(
            host='127.0.0.1',
            port=5433,
            user='safe_zone_user',
            password='0791486006@safezone',
            database='safe_zone'
        )
        
        version = await conn.fetchval("SELECT version();")
        print(f"✅ SUCCESS: Connected to {version.split(',')[0]}")
        await conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
