import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_schema():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "5433"))
    db_name = os.getenv("DB_NAME", "safe_zone")
    db_user = os.getenv("DB_USER", "safe_zone_app_user")
    db_password = os.getenv("DB_PASSWORD", "secure_app_password_2024")
    
    conn = await asyncpg.connect(
        host=db_host, port=db_port, database=db_name, 
        user=db_user, password=db_password
    )
    
    print("🔧 FIXING SAVED_POSTS TABLE SCHEMA")
    print("=" * 50)
    
    # Check current table structure
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'saved_posts'
        ORDER BY ordinal_position;
    """)
    
    print("Current saved_posts structure:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # Add saved_at column if it doesn't exist
    await conn.execute("""
        ALTER TABLE saved_posts 
        ADD COLUMN IF NOT EXISTS saved_at TIMESTAMPTZ DEFAULT NOW();
    """)
    
    print("✅ Added saved_at column")
    
    # Verify the fix
    columns_after = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'saved_posts'
        ORDER BY ordinal_position;
    """)
    
    print("\nFixed saved_posts structure:")
    for col in columns_after:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_schema())
