import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_tables():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    table_names = [t['table_name'] for t in tables]
    print('Existing tables:', table_names)
    
    if 'post_likes' in table_names:
        print('✅ post_likes table exists')
        # Check structure
        structure = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'post_likes'")
        print('Post_likes structure:')
        for col in structure:
            print(f"  {col['column_name']}: {col['data_type']}")
    else:
        print('❌ post_likes table missing')
        
    if 'comment_likes' in table_names:
        print('✅ comment_likes table exists')
    else:
        print('❌ comment_likes table missing')
        
    await conn.close()

asyncio.run(check_tables())
