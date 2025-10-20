#!/usr/bin/env python3
"""
Script to update posts table for audio support
Phase 3, Item 1: Audio Post Support
"""

import asyncpg
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

async def update_posts_for_audio():
    """Update posts table to support audio files"""
    
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
        
        # Add audio-related columns to posts table
        print("🗂️ Updating posts table for audio support...")
        
        # Add media-related columns
        await conn.execute("""
            ALTER TABLE posts 
            ADD COLUMN IF NOT EXISTS audio_url VARCHAR(500),
            ADD COLUMN IF NOT EXISTS audio_duration INTEGER,
            ADD COLUMN IF NOT EXISTS file_size INTEGER,
            ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100);
        """)
        
        # Update content_type enum values in application logic (we'll handle this in schemas)
        print("✅ Posts table updated for audio support!")
        print("   - audio_url: Added for storing audio file URLs")
        print("   - audio_duration: Added for storing audio duration in seconds") 
        print("   - file_size: Added for storing file size in bytes")
        print("   - mime_type: Added for storing MIME type")
        
        # Create a separate table for file upload tracking (optional but recommended)
        print("🗂️ Creating file_uploads table for tracking...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS file_uploads (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                post_id UUID REFERENCES posts(id) ON DELETE SET NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_url VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                duration INTEGER,  -- For audio/video files
                upload_status VARCHAR(20) DEFAULT 'completed',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        
        # Enable RLS on file_uploads
        print("🔒 Enabling RLS on file_uploads...")
        await conn.execute("ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;")
        
        # Create RLS policies for file_uploads
        print("📝 Creating RLS policies for file_uploads...")
        await conn.execute("""
            CREATE POLICY user_view_own_file_uploads ON file_uploads
            FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        await conn.execute("""
            CREATE POLICY user_insert_own_file_uploads ON file_uploads
            FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        await conn.execute("""
            CREATE POLICY user_update_own_file_uploads ON file_uploads
            FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        await conn.execute("""
            CREATE POLICY user_delete_own_file_uploads ON file_uploads
            FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::UUID);
        """)
        
        # Create indexes for better performance
        print("📊 Creating indexes...")
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);
            CREATE INDEX IF NOT EXISTS idx_file_uploads_post_id ON file_uploads(post_id);
            CREATE INDEX IF NOT EXISTS idx_file_uploads_upload_status ON file_uploads(upload_status);
            CREATE INDEX IF NOT EXISTS idx_posts_audio_url ON posts(audio_url) WHERE audio_url IS NOT NULL;
        """)
        
        print("🎉 Audio support database setup completed!")
        print("   - posts table extended for audio files")
        print("   - file_uploads table created for upload tracking")
        print("   - RLS enabled with user isolation policies")
        print("   - Performance indexes created")
        
    except Exception as e:
        print(f"❌ Error updating database for audio support: {e}")
        raise
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(update_posts_for_audio())
