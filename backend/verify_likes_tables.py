import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_likes_tables():
    database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    conn = await asyncpg.connect(database_url)
    
    print("🔍 VERIFYING LIKES TABLES...")
    
    # Check tables exist
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('post_likes', 'comment_likes')
    """)
    
    print("📋 Tables found:")
    for table in tables:
        print(f"  ✅ {table['table_name']}")
    
    # Check table structures
    for table_name in ['post_likes', 'comment_likes']:
        if any(t['table_name'] == table_name for t in tables):
            columns = await conn.fetch(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            print(f"\n📊 {table_name} structure:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
    
    # Check RLS policies
    policies = await conn.fetch("""
        SELECT tablename, policyname, permissive, roles, cmd, qual
        FROM pg_policies 
        WHERE tablename IN ('post_likes', 'comment_likes')
        ORDER BY tablename, policyname
    """)
    
    print(f"\n🔒 RLS Policies ({len(policies)} found):")
    for policy in policies:
        print(f"  - {policy['tablename']}.{policy['policyname']}: {policy['cmd']}")
    
    await conn.close()

asyncio.run(verify_likes_tables())
