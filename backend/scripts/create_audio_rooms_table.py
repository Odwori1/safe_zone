#!/usr/bin/env python3
"""
Script to create audio rooms tables for Safe Zone backend using postgres user
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Use postgres superuser credentials to create tables
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("DB_NAME", "safe_zone")
DB_USER = "postgres"  # Use postgres superuser
DB_PASSWORD = "0791486006@safezone"  # Postgres user password

async def create_audio_rooms_tables():
    """Create audio rooms and participants tables using postgres user"""
    print(f"Connecting to database as postgres user: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    try:
        print("Creating audio_rooms table...")
        
        # Create audio_rooms table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS audio_rooms (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                visibility VARCHAR(50) NOT NULL DEFAULT 'public', -- public, private, followers
                max_participants INTEGER NOT NULL DEFAULT 10,
                room_type VARCHAR(50) NOT NULL DEFAULT 'support', -- support, discussion, social
                is_active BOOLEAN NOT NULL DEFAULT true,
                is_locked BOOLEAN NOT NULL DEFAULT false,
                locked_by UUID REFERENCES users(id) ON DELETE SET NULL,
                lock_reason TEXT,
                locked_at TIMESTAMPTZ,
                current_participants INTEGER NOT NULL DEFAULT 0,
                host_username VARCHAR(255),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        ''')
        
        print("Creating audio_room_participants table...")
        
        # Create audio_room_participants table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS audio_room_participants (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                room_id UUID NOT NULL REFERENCES audio_rooms(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                left_at TIMESTAMPTZ,
                is_speaker BOOLEAN NOT NULL DEFAULT false,
                is_moderator BOOLEAN NOT NULL DEFAULT false,
                UNIQUE(room_id, user_id)
            );
        ''')
        
        print("Creating indexes...")
        
        # Create indexes for better performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_audio_rooms_created_by 
            ON audio_rooms(created_by);
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_audio_rooms_visibility 
            ON audio_rooms(visibility, is_active);
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_audio_room_participants_room 
            ON audio_room_participants(room_id);
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_audio_room_participants_user 
            ON audio_room_participants(user_id);
        ''')
        
        print("✅ Audio rooms tables created successfully!")
        
        # Grant permissions to safe_zone_app_user
        print("Granting permissions to safe_zone_app_user...")
        await conn.execute('''
            GRANT ALL PRIVILEGES ON TABLE audio_rooms TO safe_zone_app_user;
        ''')
        await conn.execute('''
            GRANT ALL PRIVILEGES ON TABLE audio_room_participants TO safe_zone_app_user;
        ''')
        await conn.execute('''
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;
        ''')
        
        print("✅ Permissions granted to safe_zone_app_user!")
        
    except Exception as e:
        print(f"❌ Error creating audio rooms tables: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_audio_rooms_tables())
