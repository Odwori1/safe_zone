#!/usr/bin/env python3
"""
Check current posts table schema
"""

import asyncio
import asyncpg
from app.core.config import settings

async def check_posts_schema():
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        print("📊 CURRENT POSTS TABLE SCHEMA:")
        print("=" * 50)
        
        # Get posts table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'posts'
            ORDER BY ordinal_position;
        """)
        
        for column in columns:
            print(f"  {column['column_name']}: {column['data_type']} "
                  f"(nullable: {column['is_nullable']}, default: {column['column_default']})")
        
        # Check current content_type enum values
        print("\n📝 CURRENT CONTENT_TYPE VALUES:")
        content_types = await conn.fetch("""
            SELECT DISTINCT content_type FROM posts;
        """)
        for row in content_types:
            print(f"  - {row['content_type']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(check_posts_schema())
