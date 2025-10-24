"""
TEST IF RLS IS ACTUALLY WORKING despite context issue
"""
import asyncio
from app.database.database import database

async def test_rls_actually_working():
    """Test if RLS policies are actually enforced"""
    print("🔍 TESTING IF RLS IS ACTUALLY WORKING")
    print("=" * 50)
    
    await database.connect()
    
    try:
        async with database.pool.acquire() as conn:
            # Test 1: Try to access content_reports without context
            print("1. Testing content_reports access without context:")
            try:
                reports = await conn.fetch("SELECT * FROM content_reports LIMIT 1")
                if reports:
                    print("   ❌ ABLE TO ACCESS content_reports without context - RLS NOT WORKING!")
                else:
                    print("   ✅ Cannot access content_reports without context - RLS WORKING!")
            except Exception as e:
                print(f"   ✅ RLS blocked access: {e}")
            
            # Test 2: Try with a specific user context using SET
            print("2. Testing with SET command:")
            test_user = "test-user-123"
            await conn.execute(f"SET app.current_user_id = '{test_user}'")
            current_ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Context after SET: {current_ctx}")
            
            try:
                # Try to insert a report with context
                insert_result = await conn.execute(
                    "INSERT INTO content_reports (reporter_id, content_type, content_id, reason) VALUES ($1, $2, $3, $4)",
                    test_user, 'message', '11111111-1111-1111-1111-111111111111', 'test reason'
                )
                print(f"   Insert result: {insert_result}")
                
                # Try to select it back
                user_reports = await conn.fetch(
                    "SELECT * FROM content_reports WHERE reporter_id = $1",
                    test_user
                )
                print(f"   Found {len(user_reports)} reports for user")
                
            except Exception as e:
                print(f"   RLS error: {e}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    asyncio.run(test_rls_actually_working())
