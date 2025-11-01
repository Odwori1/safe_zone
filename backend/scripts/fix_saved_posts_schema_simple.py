import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_schema():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "5433"))
    db_name = os.getenv("DB_NAME", "safe_zone")
    db_user = "postgres"  # Use postgres user for admin privileges
    db_password = "0791486006@safezone"
    
    conn = await asyncpg.connect(
        host=db_host, port=db_port, database=db_name, 
        user=db_user, password=db_password
    )
    
    print("🔧 FIXING SAVED_POSTS TABLE SCHEMA AS POSTGRES USER")
    print("=" * 50)
    
    try:
        # Add saved_at column
        await conn.execute("""
            ALTER TABLE saved_posts 
            ADD COLUMN IF NOT EXISTS saved_at TIMESTAMPTZ DEFAULT NOW();
            
            -- Update existing records
            UPDATE saved_posts SET saved_at = COALESCE(created_at, NOW()) WHERE saved_at IS NULL;
        """)
        
        print("✅ Added saved_at column and updated existing records")
        
        # Verify the fix
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'saved_posts'
            ORDER BY ordinal_position;
        """)
        
        print("\nFixed saved_posts structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_schema())
