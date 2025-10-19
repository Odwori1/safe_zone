#!/usr/bin/env python3
"""
Initialize database schema with proper tables and RLS policies
ALIGNED WITH BLUEPRINT: PostgreSQL with RLS
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def init_schema():
    """Initialize database schema with users table and RLS - BLUEPRINT ALIGNED"""
    try:
        await database.connect()
        print("✅ Database connected")
        
        async with database.pool.acquire() as conn:
            # Enable UUID extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            print("✅ UUID extension enabled")
            
            # Create users table (ALIGNED WITH BLUEPRINT)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    timezone VARCHAR(50) DEFAULT 'UTC',
                    locale VARCHAR(10) DEFAULT 'en-US',
                    role VARCHAR(20) DEFAULT 'seeker',
                    is_active BOOLEAN DEFAULT true,
                    is_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    last_login TIMESTAMPTZ
                );
            """)
            print("✅ Users table created")
            
            # Enable Row Level Security (BLUEPRINT: RLS IMPLEMENTATION)
            await conn.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled")
            
            # Create basic RLS policies (will be enhanced with auth)
            # TEMPORARY POLICIES - will be updated when auth is implemented
            await conn.execute("""
                -- Temporary policy until authentication is implemented
                CREATE POLICY "allow_all_for_now" ON users
                    FOR ALL USING (true);
            """)
            print("✅ Basic RLS policies created")
            
            # Verify table creation
            result = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'users'
            """)
            print(f"✅ Schema verification: {result} table(s) found")
            
        print("🎉 Database schema initialized successfully!")
        
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        raise
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(init_schema())
