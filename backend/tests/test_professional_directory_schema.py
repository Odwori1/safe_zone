"""
Basic test to verify professional directory schema is working
"""

import asyncio
from app.database.database import database

async def test_professional_schema():
    """Test that professional directory schema is accessible"""
    print("🧪 TESTING PROFESSIONAL DIRECTORY SCHEMA")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Check tables exist
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'professional_%'
                ORDER BY table_name;
            """)
            
            expected_tables = [
                'professional_availability',
                'professional_profiles', 
                'professional_reviews',
                'professional_services',
                'professional_verifications'
            ]
            
            actual_tables = [t['table_name'] for t in tables]
            print(f"✅ Found tables: {actual_tables}")
            
            if set(expected_tables) == set(actual_tables):
                print("✅ All expected tables exist")
            else:
                print(f"❌ Missing tables: {set(expected_tables) - set(actual_tables)}")
                return False
            
            # Test 2: Check RLS is enabled
            rls_tables = await conn.fetch("""
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename LIKE 'professional_%';
            """)
            
            all_rls_enabled = all(t['rowsecurity'] for t in rls_tables)
            if all_rls_enabled:
                print("✅ RLS enabled on all professional tables")
            else:
                print("❌ RLS not enabled on all tables")
                return False
            
            # Test 3: Check professional_directory view exists
            view_exists = await conn.fetchval("""
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = 'professional_directory';
            """)
            
            if view_exists:
                print("✅ Professional directory view exists")
            else:
                print("❌ Professional directory view missing")
                return False
            
            # Test 4: Test basic RLS context setting
            test_user_id = "test-user-123"
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, false)",
                test_user_id
            )
            ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            
            if ctx == test_user_id:
                print("✅ RLS context setting works")
            else:
                print(f"❌ RLS context failed: got {ctx}, expected {test_user_id}")
                return False
            
            print("🎉 ALL SCHEMA TESTS PASSED!")
            return True
            
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_professional_schema())
    exit(0 if success else 1)
