#!/usr/bin/env python3
"""
Fix RLS policies for file_metadata table
"""
import asyncpg
import asyncio

async def fix_file_metadata_rls():
    print("🔧 FIXING FILE_METADATA RLS POLICIES")
    print("=" * 45)
    
    # Use postgres owner credentials to modify RLS policies
    db_config = {
        'host': '127.0.0.1',
        'port': 5433,
        'database': 'safe_zone',
        'user': 'postgres',
        'password': '0791486006@safezone'
    }
    
    try:
        print("1. Connecting as postgres owner...")
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database as postgres")
        
        # Step 1: Check current RLS status and policies
        print("\n2. Checking current RLS configuration...")
        
        # Check if RLS is enabled
        rls_enabled = await conn.fetchval("""
            SELECT relrowsecurity FROM pg_class WHERE relname = 'file_metadata';
        """)
        print(f"   RLS enabled: {rls_enabled}")
        
        # Check existing policies
        policies = await conn.fetch("""
            SELECT policyname, permissive, roles, cmd, qual 
            FROM pg_policies 
            WHERE tablename = 'file_metadata';
        """)
        
        if policies:
            print("   Existing policies:")
            for policy in policies:
                print(f"     - {policy['policyname']}: {policy['cmd']}")
        else:
            print("   No RLS policies found for file_metadata")
        
        # Step 2: Drop existing policies to avoid conflicts
        print("\n3. Cleaning up existing policies...")
        policies_to_drop = [
            "file_metadata_select_policy",
            "file_metadata_insert_policy", 
            "file_metadata_update_policy",
            "file_metadata_delete_policy"
        ]
        
        for policy in policies_to_drop:
            try:
                await conn.execute(f'DROP POLICY IF EXISTS "{policy}" ON file_metadata;')
                print(f"   ✅ Dropped {policy}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {policy}: {e}")
        
        # Step 3: Create proper RLS policies
        print("\n4. Creating new RLS policies...")
        
        new_policies = [
            # Users can view their own files
            """
            CREATE POLICY "users_view_own_files" ON file_metadata
            FOR SELECT USING (user_id = current_setting('app.current_user_id')::uuid);
            """,
            
            # Users can insert their own files
            """
            CREATE POLICY "users_insert_own_files" ON file_metadata
            FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::uuid);
            """,
            
            # Users can update their own files
            """
            CREATE POLICY "users_update_own_files" ON file_metadata
            FOR UPDATE USING (user_id = current_setting('app.current_user_id')::uuid);
            """,
            
            # Users can delete their own files  
            """
            CREATE POLICY "users_delete_own_files" ON file_metadata
            FOR DELETE USING (user_id = current_setting('app.current_user_id')::uuid);
            """
        ]
        
        for policy_sql in new_policies:
            try:
                await conn.execute(policy_sql)
                print("   ✅ Policy created")
            except Exception as e:
                print(f"   ❌ Failed to create policy: {e}")
        
        # Step 4: Test the fix
        print("\n5. Testing the fix...")
        
        # Switch to app user context for testing
        await conn.close()
        
        app_db_config = {
            'host': '127.0.0.1',
            'port': 5433,
            'database': 'safe_zone',
            'user': 'safe_zone_app_user',
            'password': 'secure_app_password_2024'
        }
        
        app_conn = await asyncpg.connect(**app_db_config)
        print("   Connected as app user for testing")
        
        # Get test user
        user = await app_conn.fetchrow("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        if user:
            user_id = user['id']
            print(f"   👤 Testing with user: {user_id}")
            
            # Set current user for RLS
            await app_conn.execute(f"SET app.current_user_id = '{user_id}'")
            
            # Test S3 key insertion
            s3_key = f"uploads/{user_id}/test.mp3"
            print(f"   Testing S3 key: {s3_key}")
            
            test_id = await app_conn.fetchval("""
                INSERT INTO file_metadata (
                    user_id, s3_key, file_type, original_filename, 
                    file_size, mime_type, upload_status, moderation_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
            user_id, s3_key, "audio", "test.mp3", 1024, "audio/mpeg", "pending", "pending")
            
            print(f"   ✅ INSERT SUCCESSFUL! File ID: {test_id}")
            
            # Verify we can retrieve it
            file_data = await app_conn.fetchrow("SELECT * FROM file_metadata WHERE id = $1", test_id)
            print(f"   📄 Retrieved file: {file_data['original_filename']}")
            
            # Clean up
            await app_conn.execute("DELETE FROM file_metadata WHERE id = $1", test_id)
            print("   🧹 Test data cleaned up")
        
        await app_conn.close()
        print("\n🎉 FILE_METADATA RLS POLICIES FIXED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_file_metadata_rls())
