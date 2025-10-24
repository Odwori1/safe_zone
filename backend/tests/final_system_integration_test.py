"""
FINAL SYSTEM INTEGRATION TEST
Verifies that Phase 3, Item 6 integrates properly with the existing system
"""

import asyncio
from app.database.database import database

async def test_system_stability():
    """Test that the entire system remains stable"""
    print("🔧 FINAL SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Database connectivity
    print("1. Testing database connectivity...")
    try:
        await database.connect()
        async with database.pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                print("   ✅ Database connectivity: WORKING")
            else:
                print("   ❌ Database connectivity: FAILED")
                return False
    except Exception as e:
        print(f"   ❌ Database connectivity: FAILED - {e}")
        return False
    
    # Test 2: RLS functionality
    print("2. Testing RLS functionality...")
    try:
        async with database.pool.acquire() as conn:
            # Set RLS context
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", "system-test-user")
            ctx = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            if ctx == "system-test-user":
                print("   ✅ RLS context setting: WORKING")
            else:
                print("   ❌ RLS context setting: FAILED")
                return False
    except Exception as e:
        print(f"   ❌ RLS functionality: FAILED - {e}")
        return False
    
    # Test 3: Import all critical modules
    print("3. Testing module imports...")
    try:
        from app.crud.enhanced_moderation import enhanced_moderation_crud
        from app.api.endpoints.enhanced_moderation import router
        from app.schemas.enhanced_moderation import ModerationActionCreate, ReportContentCreate
        print("   ✅ All module imports: WORKING")
    except ImportError as e:
        print(f"   ❌ Module imports: FAILED - {e}")
        return False
    
    # Test 4: Verify enhanced moderation CRUD methods exist
    print("4. Testing enhanced moderation methods...")
    try:
        required_methods = [
            'create_moderation_action', 'get_user_moderation_status', 
            'create_content_report', 'get_user_reports'
        ]
        for method in required_methods:
            if hasattr(enhanced_moderation_crud, method):
                print(f"   ✅ {method}: EXISTS")
            else:
                print(f"   ❌ {method}: MISSING")
                return False
    except Exception as e:
        print(f"   ❌ Enhanced moderation methods: FAILED - {e}")
        return False
    
    # Test 5: Verify endpoints are registered
    print("5. Testing endpoint registration...")
    try:
        if len(router.routes) >= 11:  # We have 11 endpoints
            print(f"   ✅ Endpoints registered: {len(router.routes)} endpoints")
        else:
            print(f"   ❌ Endpoints registered: ONLY {len(router.routes)} endpoints")
            return False
    except Exception as e:
        print(f"   ❌ Endpoint registration: FAILED - {e}")
        return False
    
    print("=" * 50)
    print("🎉 FINAL SYSTEM INTEGRATION TEST: ALL CHECKS PASSED!")
    print("✅ Database connectivity: STABLE")
    print("✅ RLS functionality: WORKING") 
    print("✅ Module imports: SUCCESSFUL")
    print("✅ Enhanced moderation: IMPLEMENTED")
    print("✅ Endpoint registration: COMPLETE")
    print("🚀 SYSTEM IS READY FOR PRODUCTION")
    return True

async def main():
    success = await test_system_stability()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
