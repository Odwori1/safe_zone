#!/usr/bin/env python3
"""
CHECK DATABASE INITIALIZATION
"""
import asyncio
from app.database.database import database, init_db

async def check_database_init():
    """Check database initialization"""
    
    print("🔌 CHECKING DATABASE INITIALIZATION")
    print("=" * 50)
    
    try:
        print("1. INITIALIZING DATABASE...")
        await init_db()
        
        print("2. CHECKING CONNECTION POOL...")
        if database.pool:
            print("✅ Database pool initialized")
            
            # Test a simple query
            conn = await database.pool.acquire()
            try:
                result = await conn.fetchval("SELECT version();")
                print(f"✅ Database connection working: {result.split(',')[0]}")
                
                # Check current user
                current_user = await conn.fetchval("SELECT current_user;")
                print(f"   Connected as: {current_user}")
                
            finally:
                await database.pool.release(conn)
        else:
            print("❌ Database pool not initialized")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database_init())
