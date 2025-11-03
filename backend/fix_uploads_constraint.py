#!/usr/bin/env python3
"""
Fix the uploads system S3 key constraint
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_uploads_constraint():
    print("🔧 FIXING UPLOADS SYSTEM CONSTRAINT")
    print("=" * 45)
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Step 1: Check the current constraint
        print("\n1. Checking current constraint...")
        constraints = await conn.fetch("""
            SELECT conname, consrc 
            FROM pg_constraint 
            WHERE conname = 'valid_s3_key'
            AND conrelid = 'file_metadata'::regclass;
        """)
        
        if constraints:
            for constraint in constraints:
                print(f"   Constraint: {constraint['conname']}")
                print(f"   Definition: {constraint['consrc']}")
        else:
            print("   ❌ Constraint 'valid_s3_key' not found")
        
        # Step 2: Check what S3 keys are currently valid
        print("\n2. Checking current file_metadata entries...")
        files = await conn.fetch("SELECT s3_key FROM file_metadata LIMIT 5;")
        if files:
            print("   Current S3 keys:")
            for file in files:
                print(f"     - {file['s3_key']}")
        else:
            print("   No existing file_metadata entries")
        
        # Step 3: Drop and recreate the constraint with proper validation
        print("\n3. Fixing the constraint...")
        
        # Drop the existing constraint
        await conn.execute("ALTER TABLE file_metadata DROP CONSTRAINT IF EXISTS valid_s3_key;")
        print("   ✅ Dropped old constraint")
        
        # Create a more permissive constraint
        await conn.execute("""
            ALTER TABLE file_metadata 
            ADD CONSTRAINT valid_s3_key 
            CHECK (s3_key IS NULL OR (s3_key ~ '^[a-zA-Z0-9_\\-\\./]+$' AND length(s3_key) > 0));
        """)
        print("   ✅ Created new permissive constraint")
        
        # Step 4: Test the fix
        print("\n4. Testing uploads fix...")
        
        # Get a test user
        user = await conn.fetchrow("SELECT id FROM users WHERE email = 'developer_test@example.com'")
        user_id = user['id'] if user else None
        
        if user_id:
            # Test inserting a file_metadata record
            test_file_id = await conn.fetchval("""
                INSERT INTO file_metadata (
                    user_id, s3_key, file_type, original_filename, 
                    file_size, mime_type, upload_status, moderation_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
            user_id, 
            f"uploads/{user_id}/test.mp3",  # This should now work
            "audio", "test.mp3", 1024, "audio/mpeg", "pending", "pending")
            
            print(f"   ✅ File metadata insertion SUCCESSFUL! ID: {test_file_id}")
            
            # Clean up
            await conn.execute("DELETE FROM file_metadata WHERE id = $1", test_file_id)
            print("   🧹 Test data cleaned up")
        
        await conn.close()
        print("\n🎉 UPLOADS CONSTRAINT FIXED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Constraint fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_uploads_constraint())
