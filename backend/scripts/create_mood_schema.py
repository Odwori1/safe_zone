#!/usr/bin/env python3
"""
Script to create mood_entries table with RLS
Phase 2, Item 7: Mood Tracker Implementation
"""

import asyncpg
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

async def create_mood_table():
    """Create mood_entries table with RLS policies"""
    
    conn = None
    try:
        # Connect to PostgreSQL
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        # Enable UUID extension if not already enabled
        print("📦 Enabling UUID extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Create mood_entries table
        print("🗂️ Creating mood_entries table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS mood_entries (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                mood VARCHAR(50) NOT NULL,
                intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable Row Level Security
        print("🔒 Enabling RLS on mood_entries...")
        await conn.execute("ALTER TABLE mood_entries ENABLE ROW LEVEL SECURITY;")
        
        # Create RLS policies
        print("📝 Creating RLS policies...")
        
        # Policy: Users can only view their own mood entries
        await conn.execute("""
            CREATE POLICY user_view_own_mood_entries ON mood_entries
            FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only insert their own mood entries
        await conn.execute("""
            CREATE POLICY user_insert_own_mood_entries ON mood_entries
            FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only update their own mood entries
        await conn.execute("""
            CREATE POLICY user_update_own_mood_entries ON mood_entries
            FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Policy: Users can only delete their own mood entries
        await conn.execute("""
            CREATE POLICY user_delete_own_mood_entries ON mood_entries
            FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Create indexes for better performance
        print("📊 Creating indexes...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_mood_entries_user_id ON mood_entries(user_id);
            CREATE INDEX IF NOT EXISTS idx_mood_entries_created_at ON mood_entries(created_at);
            CREATE INDEX IF NOT EXISTS idx_mood_entries_mood ON mood_entries(mood);
        """)
        
        print("✅ Mood tracker schema created successfully!")
        print("   - mood_entries table created")
        print("   - RLS enabled with user isolation policies")
        print("   - Performance indexes created")
        
    except Exception as e:
        print(f"❌ Error creating mood schema: {e}")
        raise
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(create_mood_table())
