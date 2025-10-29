#!/usr/bin/env python3
"""
Create user relationships tables following exact project patterns
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_user_relationships_schema():
    """Create user relationships tables with RLS - FOLLOWING EXACT PATTERN"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # First, let's check if tables already exist
            print("🔍 Checking existing tables...")
            
            existing_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('user_relationships', 'user_reports')
            """)
            
            if existing_tables:
                print(f"⚠️ Tables already exist: {[t['table_name'] for t in existing_tables]}")
                return

            # Create user_relationships table - FOLLOWING EXACT PATTERN
            print("🔄 Creating user_relationships table...")
            await conn.execute("""
                CREATE TABLE user_relationships (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('follow', 'block')),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    
                    -- Prevent duplicate relationships
                    UNIQUE(follower_id, following_id, relationship_type),
                    
                    -- Prevent self-follow/self-block
                    CONSTRAINT no_self_relationship CHECK (follower_id != following_id)
                );
            """)
            print("✅ Created user_relationships table")

            # Create user_reports table - FOLLOWING EXACT PATTERN
            print("🔄 Creating user_reports table...")
            await conn.execute("""
                CREATE TABLE user_reports (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    reported_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    report_reason TEXT NOT NULL,
                    report_details TEXT,
                    report_status TEXT DEFAULT 'pending' CHECK (report_status IN ('pending', 'reviewed', 'resolved', 'dismissed')),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            print("✅ Created user_reports table")

            # Add unique constraint for pending reports
            await conn.execute("""
                ALTER TABLE user_reports ADD CONSTRAINT unique_pending_report 
                UNIQUE (reporter_id, reported_user_id) 
                WHERE (report_status = 'pending');
            """)
            print("✅ Added unique constraint for user_reports")

            # Enable Row Level Security - FOLLOWING EXACT PATTERN
            await conn.execute("ALTER TABLE user_relationships ENABLE ROW LEVEL SECURITY;")
            await conn.execute("ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;")
            print("✅ RLS enabled for both tables")

            # Create RLS policies using app.current_user_id (CONSISTENT WITH SYSTEM)
            # User Relationships Policies
            await conn.execute("""
                -- Users can see relationships they're involved in
                CREATE POLICY "users_view_relationships" ON user_relationships
                    FOR SELECT USING (
                        follower_id = current_setting('app.current_user_id', true)::uuid OR
                        following_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)

            await conn.execute("""
                -- Users can create relationships where they are the follower
                CREATE POLICY "users_create_relationships" ON user_relationships
                    FOR INSERT WITH CHECK (
                        follower_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)

            await conn.execute("""
                -- Users can delete relationships they created
                CREATE POLICY "users_delete_relationships" ON user_relationships
                    FOR DELETE USING (
                        follower_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)
            print("✅ RLS policies created for user_relationships")

            # User Reports Policies
            await conn.execute("""
                -- Users can see reports they created
                CREATE POLICY "users_view_reports" ON user_reports
                    FOR SELECT USING (
                        reporter_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)

            await conn.execute("""
                -- Users can create reports where they are the reporter
                CREATE POLICY "users_create_reports" ON user_reports
                    FOR INSERT WITH CHECK (
                        reporter_id = current_setting('app.current_user_id', true)::uuid
                    );
            """)
            print("✅ RLS policies created for user_reports")

            # Create indexes - FOLLOWING EXACT PATTERN
            await conn.execute("CREATE INDEX idx_user_relationships_follower ON user_relationships(follower_id, relationship_type);")
            await conn.execute("CREATE INDEX idx_user_relationships_following ON user_relationships(following_id, relationship_type);")
            await conn.execute("CREATE INDEX idx_user_relationships_bidirectional ON user_relationships(follower_id, following_id);")
            await conn.execute("CREATE INDEX idx_user_reports_reporter ON user_reports(reporter_id);")
            await conn.execute("CREATE INDEX idx_user_reports_reported ON user_reports(reported_user_id);")
            await conn.execute("CREATE INDEX idx_user_reports_status ON user_reports(report_status);")
            print("✅ Indexes created")

            # Create updated_at trigger function and trigger
            await conn.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)

            await conn.execute("""
                CREATE TRIGGER update_user_reports_updated_at 
                    BEFORE UPDATE ON user_reports 
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """)
            print("✅ Created updated_at trigger for user_reports")

            # Verify tables were created
            print("🔍 Verifying table creation...")
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('user_relationships', 'user_reports')
            """)
            
            print(f"✅ Created tables: {[t['table_name'] for t in tables]}")

        print("🎉 User relationships schema created successfully!")

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_user_relationships_schema())
