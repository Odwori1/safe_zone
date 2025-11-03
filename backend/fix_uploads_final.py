#!/usr/bin/env python3
"""
Fix uploads constraint with correct database credentials
"""
import asyncpg
import asyncio

async def fix_uploads_final():
    print("🔧 FIXING UPLOADS CONSTRAINT - FINAL VERSION")
    print("=" * 50)
    
    # Use the correct credentials from your .env file
    db_config = {
        'host': '127.0.0.1',
        'port': 5433,
        'database': 'safe_zone',
        'user': 'safe_zone_app_user', 
        'password': 'secure_app_password_2024'
    }
    
    try:
        print("1. Connecting to database...")
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
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
        else:
            print("   No 'valid_s3_key' constraint found")
        
        # Step 2: Drop the constraint
        print("\n3. Dropping constraint...")
        await conn.execute("ALTER TABLE file_metadata DROP CONSTRAINT IF EXISTS valid_s3_key;")
        print("   ✅ Constraint dropped")
        
        # Step 3: Create new permissive constraint
        print("\n4. Creating new constraint...")
        await conn.execute("""
            ALTER TABLE file_metadata 
            ADD CONSTRAINT valid_s3_key 
            CHECK (s3_key IS NULL OR (
                s3_key ~ '^[a-zA-Z0-9_\\-\\./]+$' 
                AND length(s3_key) > 0 
                AND length(s3_key) <= 500
            ));
        """)
        print("   ✅ New constraint created")
        
        # Step 4: Test the fix
        print("\n5. Testing the fix...")
        
        # Get test user
        user = await conn.fetchrow("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        if user:
            user_id = user['id']
            print(f"   👤 Testing with user: {user_id}")
            
            # Test the exact S3 key that was failing
            test_s3_key = f"uploads/{user_id}/test.mp3"
            print(f"   Testing S3 key: {test_s3_key}")
            
            test_id = await conn.fetchval("""
                INSERT INTO file_metadata (
                    user_id, s3_key, file_type, original_filename, 
                    file_size, mime_type, upload_status, moderation_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
            user_id, 
            test_s3_key,
            "audio", "test.mp3", 1024, "audio/mpeg", "pending", "pending")
            
            print(f"   ✅ INSERT SUCCESSFUL! File ID: {test_id}")
            
            # Verify we can retrieve it
            file_data = await conn.fetchrow("SELECT * FROM file_metadata WHERE id = $1", test_id)
            print(f"   📄 Retrieved file: {file_data['original_filename']}")
            
            # Clean up
            await conn.execute("DELETE FROM file_metadata WHERE id = $1", test_id)
            print("   🧹 Test data cleaned up")
        else:
            print("   ❌ No test user found")
        
        await conn.close()
        print("\n🎉 UPLOADS CONSTRAINT FIXED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_uploads_final())
