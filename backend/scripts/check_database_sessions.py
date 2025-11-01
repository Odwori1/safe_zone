#!/usr/bin/env python3
"""
Check current database sessions and connections
"""
import asyncio
from app.database.database import database

async def check_sessions():
    """Check active database sessions"""
    await database.connect()
    
    async with database.pool.acquire() as conn:
        print("🔌 ACTIVE DATABASE SESSIONS")
        print("===========================")
        
        sessions = await conn.fetch('''
            SELECT 
                pid,
                usename,
                application_name,
                client_addr,
                state,
                query_start,
                query
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND state = 'active'
            AND query NOT LIKE '%pg_stat_activity%'
        ''')
        
        if sessions:
            for session in sessions:
                print(f"PID: {session['pid']}, User: {session['usename']}")
                print(f"App: {session['application_name']}, State: {session['state']}")
                print(f"Query: {session['query'][:100]}...")
                print("---")
        else:
            print("No active sessions found")
        
        # Check connection count
        conn_count = await conn.fetchval('SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()')
        print(f"Total connections to database: {conn_count}")

if __name__ == "__main__":
    asyncio.run(check_sessions())
