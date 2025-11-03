#!/usr/bin/env python3
"""
Fix uploads constraint using postgres owner account
"""
import asyncpg
import asyncio

async def fix_uploads_postgres():
    print("🔧 FIXING UPLOADS CONSTRAINT - POSTGRES OWNER")
    print("=" * 50)
    
    # Use postgres owner credentials
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
        
        # Step 1: Check current constraint
        print("\n2. Checking current constraint...")
        constraint = await conn.fetchrow("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conname = 'valid_s3_key'
            AND conrelid = 'file_metadata'::regclass;
        """)
        
        if constraint:
            print(f"   Found constraint: {constraint['conname']}")
            print(f"   Definition: {constraint['definition']}")
            
            # The constraint requires s3_key to start with 'users/'
            # But uploads system is generating 'uploads/user-id/filename'
        else:
            print("   No 'valid_s3_key' constraint found")
        
        # Step 2: Drop the constraint as postgres owner
        print("\n3. Dropping constraint as postgres owner...")
        await conn.execute("ALTER TABLE file_metadata DROP CONSTRAINT IF EXISTS valid_s3_key;")
        print("   ✅ Constraint dropped successfully")
        
        # Step 3: Create new flexible constraint
        print("\n4. Creating new flexible constraint...")
        await conn.execute("""
            ALTER TABLE file_metadata 
            ADD CONSTRAINT valid_s3_key 
            CHECK (
                s3_key IS NULL OR 
                (
                    (s3_key LIKE 'users/%' OR s3_key LIKE 'uploads/%') 
                    AND length(s3_key) > 0 
                    AND length(s3_key) <= 500
                    AND s3_key ~ '^[a-zA-Z0-9_\\-\\./]+$'
                )
            );
        """)
        print("   ✅ New flexible constraint created")
        print("   Now allows both 'users/' and 'uploads/' prefixes")
        
        # Step 4: Grant permissions to app user
        print("\n5. Granting permissions to app user...")
        await conn.execute("""
            GRANT ALL PRIVILEGES ON TABLE file_metadata TO safe_zone_app_user;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;
        """)
        print("   ✅ Permissions granted to safe_zone_app_user")
        
        # Step 5: Test the fix
        print("\n6. Testing the fix...")
        
        # Switch to app user context for testing
        await conn.close()
        
        # Reconnect as app user
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
            
            # Test both S3 key patterns
            test_patterns = [
                f"uploads/{user_id}/test.mp3",  # What uploads system generates
                f"users/{user_id}/test.mp3",     # What constraint expected
            ]
            
            for s3_key in test_patterns:
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
                
                # Clean up
                await app_conn.execute("DELETE FROM file_metadata WHERE id = $1", test_id)
                print("   🧹 Test data cleaned up")
        
        await app_conn.close()
        print("\n🎉 UPLOADS CONSTRAINT FIXED SUCCESSFULLY!")
        print("✅ Now accepts both 'users/' and 'uploads/' prefixes")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_uploads_postgres())
