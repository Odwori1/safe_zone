#!/usr/bin/env python3
"""
Check if Phase 3 database tables exist
"""

import asyncpg
import asyncio
import os

async def check_tables():
    # Database connection details from your .env
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5433,
        user='safe_zone_app_user',
        password='secure_app_password_2024',
        database='safe_zone'
    )
    
    # Phase 3 specific tables to check
    phase3_tables = [
        'audio_posts',
        'video_posts', 
        'file_uploads',
        'conversations',
        'messages',
        'audio_rooms',
        'audio_room_participants',
        'moderation_reports'
    ]
    
    print("🔍 CHECKING PHASE 3 DATABASE TABLES")
    print("=" * 40)
    
    for table in phase3_tables:
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
            table
        )
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"{status} {table}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tables())
