#!/usr/bin/env python3
"""
Safe Zone - Verify and Enhance User Blocks/Reports Schema
Following exact project patterns
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import database

async def verify_and_enhance_blocks_reports_schema():
    """Verify existing schema and add any missing components"""
    try:
        await database.connect()
        print("✅ Database connected")

        async with database.pool.acquire() as conn:
            # Check existing tables
            print("🔍 Checking existing tables...")
            
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name IN ('user_relationships', 'user_reports')
            """)
            
            print(f"✅ Found tables: {[t['table_name'] for t in tables]}")
            
            # Check user_relationships structure
            relationships_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user_relationships'
                ORDER BY ordinal_position
            """)
            print("📋 user_relationships columns:")
            for col in relationships_columns:
                print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
            
            # Check user_reports structure  
            reports_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user_reports'
                ORDER BY ordinal_position
            """)
            print("📋 user_reports columns:")
            for col in reports_columns:
                print(f"   - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
            
            # Check RLS policies
            rls_policies = await conn.fetch("""
                SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
                FROM pg_policies 
                WHERE tablename IN ('user_relationships', 'user_reports')
                ORDER BY tablename, policyname
            """)
            
            print("🔐 RLS Policies:")
            for policy in rls_policies:
                print(f"   - {policy['tablename']}.{policy['policyname']}: {policy['cmd']}")
            
            # Add any missing indexes for performance
            print("🔄 Creating missing indexes...")
            
            # Check and create indexes for user_relationships if missing
            existing_indexes = await conn.fetch("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'user_relationships'
            """)
            existing_index_names = [idx['indexname'] for idx in existing_indexes]
            
            if 'idx_user_relationships_block_check' not in existing_index_names:
                await conn.execute("""
                    CREATE INDEX idx_user_relationships_block_check ON user_relationships(follower_id, following_id) 
                    WHERE relationship_type = 'block'
                """)
                print("✅ Created block relationship index")
            
            # Check and create indexes for user_reports if missing  
            existing_report_indexes = await conn.fetch("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'user_reports'
            """)
            existing_report_index_names = [idx['indexname'] for idx in existing_report_indexes]
            
            if 'idx_user_reports_status' not in existing_report_index_names:
                await conn.execute("""
                    CREATE INDEX idx_user_reports_status ON user_reports(report_status, created_at)
                """)
                print("✅ Created report status index")
                
            if 'idx_user_reports_reporter' not in existing_report_index_names:
                await conn.execute("""
                    CREATE INDEX idx_user_reports_reporter ON user_reports(reporter_id, created_at)
                """)
                print("✅ Created reporter index")
            
            print("🎉 Schema verification complete!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(verify_and_enhance_blocks_reports_schema())
