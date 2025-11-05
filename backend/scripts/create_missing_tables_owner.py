#!/usr/bin/env python3
"""
Create missing Phase 3 tables using owner credentials
"""

import asyncpg
import asyncio

async def create_missing_tables():
    """Create missing tables with proper owner credentials"""
    
    # Connect as postgres owner
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=5433,
        user='postgres',
        password='0791486006@safezone',
        database='safe_zone'
    )
    
    print("🔧 CREATING MISSING TABLES WITH OWNER CREDENTIALS")
    print("=" * 50)
    
    try:
        # First, check what tables exist
        existing_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        existing_table_names = [t['table_name'] for t in existing_tables]
        
        # Create moderation_reports table if missing
        if 'moderation_reports' not in existing_table_names:
            print("📋 CREATING moderation_reports TABLE...")
            
            await conn.execute("""
                CREATE TABLE moderation_reports (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    reported_content_type VARCHAR(50) NOT NULL,
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
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX idx_moderation_reports_reporter ON moderation_reports(reporter_id);
                CREATE INDEX idx_moderation_reports_status ON moderation_reports(status);
                CREATE INDEX idx_moderation_reports_content ON moderation_reports(reported_content_type, reported_content_id);
            """)
            
            print("✅ Created moderation_reports table")
        else:
            print("✅ moderation_reports table already exists")
        
        # Check if we need to create any other missing tables
        # Note: We already have content_reports table based on your output
        
        # Grant permissions to the app user
        print("\n🔐 GRANTING PERMISSIONS TO APP USER...")
        await conn.execute("""
            GRANT ALL PRIVILEGES ON TABLE moderation_reports TO safe_zone_app_user;
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;
        """)
        
        print("✅ Permissions granted to safe_zone_app_user")
        
        # Verify the table was created
        verify_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('moderation_reports')
        """)
        
        print(f"\n✅ VERIFICATION: {len(verify_tables)} tables created successfully")
        for table in verify_tables:
            print(f"   - {table['table_name']}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await conn.close()
    
    print("\n🎉 Table creation completed!")

if __name__ == "__main__":
    asyncio.run(create_missing_tables())
