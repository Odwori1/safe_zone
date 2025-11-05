#!/usr/bin/env python3
"""
Fix missing Phase 3 database tables
"""

import asyncpg
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def fix_missing_tables():
    """Create missing Phase 3 tables"""
    
    # Database connection
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5433,
        user='safe_zone_app_user',
        password='secure_app_password_2024',
        database='safe_zone'
    )
    
    print("🔧 FIXING MISSING PHASE 3 TABLES")
    print("=" * 50)
    
    # Check what tables actually exist
    existing_tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    print("📋 EXISTING TABLES:")
    for table in existing_tables:
        print(f"  ✅ {table['table_name']}")
    
    # Create moderation_reports table if missing
    if not any(t['table_name'] == 'moderation_reports' for t in existing_tables):
        print("\n📋 CREATING moderation_reports TABLE...")
        await conn.execute("""
            CREATE TABLE moderation_reports (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                reported_content_type VARCHAR(50) NOT NULL, -- 'post', 'comment', 'user', 'message'
                reported_content_id UUID NOT NULL,
                report_reason VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
                severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
                moderator_notes TEXT,
                resolved_at TIMESTAMPTZ,
                resolved_by UUID REFERENCES users(id),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            -- RLS Policies
            ALTER TABLE moderation_reports ENABLE ROW LEVEL SECURITY;
            
            -- Users can view their own reports
            CREATE POLICY user_view_own_reports ON moderation_reports
                FOR SELECT USING (reporter_id = current_user_id());
                
            -- Users can create reports
            CREATE POLICY user_create_reports ON moderation_reports
                FOR INSERT WITH CHECK (reporter_id = current_user_id());
                
            -- Moderators can view all reports
            CREATE POLICY moderators_view_all_reports ON moderation_reports
                FOR SELECT USING (is_moderator());
                
            -- Moderators can update reports
            CREATE POLICY moderators_update_reports ON moderation_reports
                FOR UPDATE USING (is_moderator());
        """)
        print("✅ Created moderation_reports table")
    
    # Note: We don't need separate audio_posts and video_posts tables
    # Our system uses the main posts table with file attachments
    print("\n📝 Note: Using main 'posts' table for audio/video posts with file attachments")
    
    await conn.close()
    print("\n🎉 Database schema fixes completed!")

if __name__ == "__main__":
    asyncio.run(fix_missing_tables())
