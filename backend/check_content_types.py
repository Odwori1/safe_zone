import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_content_types():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    
    # Check the posts table structure
    table_info = await conn.fetch("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'posts'
    """)
    print("Posts table columns:")
    for col in table_info:
        print(f"  {col['column_name']}: {col['data_type']} ({'nullable' if col['is_nullable'] == 'YES' else 'not null'})")
    
    # Check distinct content_types
    content_types = await conn.fetch("SELECT DISTINCT content_type FROM posts")
    print("\nExisting content_types in posts:")
    for ct in content_types:
        print(f"  - {ct['content_type']}")
    
    # Check if there are any video posts
    video_posts = await conn.fetch("SELECT COUNT(*) as count FROM posts WHERE content_type = 'video'")
    print(f"\nVideo posts count: {video_posts[0]['count']}")
    
    await conn.close()

asyncio.run(check_content_types())
