#!/usr/bin/env python3
"""
Verify Crisis System RLS is working properly
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_crisis_rls():
    """Verify RLS is working for crisis tables"""
    try:
        database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        conn = await asyncpg.connect(database_url)
        
        print("🔍 Verifying Crisis System RLS...")
        
        # Get a user for testing
        user_id = await conn.fetchval("SELECT id FROM users LIMIT 1;")
        if not user_id:
            print("❌ No users found for testing")
            return
        
        print(f"🔧 Testing with user: {user_id}")
        await conn.execute("SELECT set_current_user_id($1);", user_id)
        
        # Test each table
        tables = [
            ('emergency_contacts', 'user_emergency_contacts_policy'),
            ('crisis_resources', 'view_crisis_resources_policy'),
            ('safety_plans', 'user_safety_plans_policy'),
            ('wellness_checkins', 'user_wellness_checkins_policy'),
            ('crisis_alerts', 'user_crisis_alerts_policy')
        ]
        
        for table_name, expected_policy in tables:
            try:
                # Try to select from table (should work with RLS context)
                result = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                print(f"✅ {table_name}: RLS allows access (count: {result})")
                
                # Check policy exists
                policy_exists = await conn.fetchval("""
                    SELECT 1 FROM pg_policies 
                    WHERE tablename = $1 AND policyname = $2
                """, table_name, expected_policy)
                
                if policy_exists:
                    print(f"   ✅ Policy '{expected_policy}' exists")
                else:
                    print(f"   ❌ Policy '{expected_policy}' missing")
                    
            except Exception as e:
                print(f"❌ {table_name}: RLS blocked access - {e}")
        
        await conn.close()
        print("\n🎉 RLS verification completed!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_crisis_rls())
