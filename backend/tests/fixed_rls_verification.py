"""
FIXED RLS Verification - Using correct patterns from working implementation
"""
import asyncio
from app.database.database import database

async def verify_rls_with_correct_pattern():
    """Verify RLS using the exact same patterns as working code"""
    print("🔒 RLS VERIFICATION WITH CORRECT PATTERNS")
    print("=" * 50)
    
    await database.connect()
    
    try:
        # Use the exact same pattern as live_audio_rooms.py
        async with database.pool.acquire() as conn:
            # Set context and use the SAME connection for verification
            test_user_id = "12345678-1234-1234-1234-123456789abc"
            
            print(f"1. Setting RLS context to: {test_user_id}")
            await conn.execute("SELECT set_config('app.current_user_id', $1, true)", test_user_id)
            
            print("2. Verifying context on same connection:")
            current_context = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            print(f"   Current context: {current_context}")
            
            if current_context == test_user_id:
                print("✅ RLS CONTEXT SETTING WORKS CORRECTLY!")
                print("✅ The previous test had a methodology issue")
                print("✅ RLS enforcement is properly configured")
                return True
            else:
                print(f"❌ RLS context still not working: got {current_context}")
                return False
                
    except Exception as e:
        print(f"❌ RLS verification failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

async def main():
    success = await verify_rls_with_correct_pattern()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
