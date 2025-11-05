#!/usr/bin/env python3
"""
Check what Phase 3 tables actually exist and what we need
"""

import asyncpg
import asyncio

async def check_actual_tables():
    """Check what tables we actually have with owner credentials"""
    
    # Connect as postgres owner
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5433,
        user='postgres',
        password='0791486006@safezone',
        database='safe_zone'
    )
    
    print("🔍 CHECKING ACTUAL TABLE STATUS")
    print("=" * 50)
    
    # Check all tables
    tables = await conn.fetch("""
        SELECT table_name, table_schema
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    print(f"📋 TOTAL TABLES: {len(tables)}")
    for table in tables:
        print(f"  {table['table_name']}")
    
    # Check if we have the tables we need for Phase 3
    phase3_critical_tables = [
        'file_uploads', 'conversations', 'messages', 
        'audio_rooms', 'audio_room_participants', 'content_reports'
    ]
    
    print("\n🎯 PHASE 3 CRITICAL TABLES STATUS:")
    existing_tables = [t['table_name'] for t in tables]
    for table in phase3_critical_tables:
        status = "✅ EXISTS" if table in existing_tables else "❌ MISSING"
        print(f"  {status} {table}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_actual_tables())
