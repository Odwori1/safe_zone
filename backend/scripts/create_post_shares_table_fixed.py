#!/usr/bin/env python3
"""
Create post_shares table following EXACT project patterns (same as post_likes)
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def create_post_shares_table():
    """Create post_shares table with RLS - FOLLOWING EXACT PROJECT PATTERNS"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Use the EXACT same pattern as the working script
            user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")

            if not user_id:
                print("❌ No users found in database. Cannot set RLS context.")
                return

            print(f"🔧 Setting RLS context with user_id: {user_id}")
            await conn.execute("SELECT set_current_user_id($1);", user_id)

            # Check if table already exists - FOLLOWING EXACT PATTERN
            existing_tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'post_shares'
            """)

            existing_table_names = [t['table_name'] for t in existing_tables]
            print(f"🔍 Existing tables: {existing_table_names}")

            # Create post_shares table if it doesn't exist
            if 'post_shares' not in existing_table_names:
                print("🔄 Creating post_shares table...")
                await conn.execute("""
                    CREATE TABLE post_shares (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        post_id UUID NOT NULL,
                        user_id UUID NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        UNIQUE(post_id, user_id)
                    );
                """)
                print("✅ Created post_shares table")
            else:
                print("✅ post_shares table already exists")

            # Enable RLS - FOLLOWING EXACT PATTERN
            if 'post_shares' not in existing_table_names:
                await conn.execute("ALTER TABLE post_shares ENABLE ROW LEVEL SECURITY;")
                print("✅ RLS enabled for post_shares")

            # Create RLS policies for post_shares - FOLLOWING EXACT PATTERN (same as post_likes)
            if 'post_shares' not in existing_table_names:
                await conn.execute("""
                    CREATE POLICY "users_view_post_shares" ON post_shares
                        FOR SELECT USING (
                            EXISTS (
                                SELECT 1 FROM posts
                                WHERE posts.id = post_shares.post_id
                                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                            )
                        );
                """)

                await conn.execute("""
                    CREATE POLICY "users_create_post_shares" ON post_shares
                        FOR INSERT WITH CHECK (
                            user_id = current_setting('app.current_user_id', true)::uuid
                            AND EXISTS (
                                SELECT 1 FROM posts
                                WHERE posts.id = post_shares.post_id
                                AND (posts.visibility = 'public' OR posts.user_id = current_setting('app.current_user_id', true)::uuid)
                            )
                        );
                """)

                await conn.execute("""
                    CREATE POLICY "users_delete_post_shares" ON post_shares
                        FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::uuid);
                """)
                print("✅ RLS policies created for post_shares")

            # Create indexes (same as post_likes)
            if 'post_shares' not in existing_table_names:
                await conn.execute("CREATE INDEX idx_post_shares_post_id ON post_shares(post_id);")
                await conn.execute("CREATE INDEX idx_post_shares_user_id ON post_shares(user_id);")
                print("✅ Indexes created for post_shares")

            # Verify final state
            final_tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'post_shares'
            """)

            final_table_names = [t['table_name'] for t in final_tables]
            print(f"🎉 Final tables: {final_table_names}")

        print("✅ Post shares table setup completed successfully!")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(create_post_shares_table())
