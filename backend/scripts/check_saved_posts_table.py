import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_table():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "5433"))
    db_name = os.getenv("DB_NAME", "safe_zone")
    db_user = os.getenv("DB_USER", "safe_zone_app_user")
    db_password = os.getenv("DB_PASSWORD", "secure_app_password_2024")
    
    conn = await asyncpg.connect(
        host=db_host, port=db_port, database=db_name, 
        user=db_user, password=db_password
    )
    
    # Check if saved_posts table exists
    table_exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'saved_posts'
        );
    """)
    
    if table_exists:
        print("✅ saved_posts table exists")
        # Check structure
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'saved_posts'
            ORDER BY ordinal_position;
        """)
        print("Table structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
    else:
        print("❌ saved_posts table does not exist")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_table())
