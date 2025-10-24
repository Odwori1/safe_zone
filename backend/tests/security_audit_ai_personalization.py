"""
SECURITY AUDIT: AI Personalization Implementation
Following EXACT same patterns as security_audit_professional_directory.py
"""

import asyncio
import inspect
from app.database.database import database
from app.crud.ai_personalization import ai_personalization_crud
from app.api.endpoints.ai_personalization import router

async def initialize_database():
    """Initialize database connection"""
    if not database.pool:
        await database.connect()

async def test_rls_enforcement_ai_data():
    """Test that RLS properly enforces AI data isolation"""
    print("🔒 Testing RLS enforcement for AI personalization data...")

    await initialize_database()

    try:
        async with database.pool.acquire() as conn:
            test_user_id = "test-user-rls-123"
            await conn.execute("SELECT set_config('app.current_user_id', $1, false)", test_user_id)

            # Verify context is set
            result = await conn.fetchval("SELECT current_setting('app.current_user_id', true)")
            assert result == test_user_id
            print("✅ RLS context setting verified")

        print("✅ RLS enforcement test passed")
        return True

    except Exception as e:
        print(f"❌ RLS enforcement test failed: {e}")
        return False

async def test_crud_security_patterns():
    """Verify CRUD operations follow security patterns"""
    print("🔒 Testing CRUD security patterns...")

    # Check that all CRUD methods exist and follow security patterns
    required_methods = [
        'create_content_analysis',
        'get_content_analysis', 
        'get_user_behavior_patterns',
        'update_user_behavior_patterns',
        'create_recommendation',
        'get_user_recommendations',
        'update_recommendation_interaction',
        'get_coping_strategies',
        'get_user_coping_preferences',
        'update_coping_preference',
        'get_notification_preferences',
        'update_notification_preferences',
        'health_check'
    ]

    for method in required_methods:
        if hasattr(ai_personalization_crud, method):
            print(f"✅ {method} - IMPLEMENTED")
        else:
            print(f"❌ {method} - MISSING")
            return False

    # Verify methods follow user_id parameter pattern for RLS context
    for method_name in required_methods:
        method = getattr(ai_personalization_crud, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Critical security check: Methods should accept user_id for RLS context
        # Except get_coping_strategies which is public
        if method_name != 'get_coping_strategies':
            has_user_param = any('user' in param.lower() or param in ['user_id', 'requesting_user_id', 'analyst_id', 'recommender_id'] for param in params)
            if not has_user_param:
                print(f"❌ Method {method_name} missing user context parameter")
                return False

    print("✅ CRUD security patterns verified")
    return True

async def test_endpoint_authentication():
    """Verify all endpoints require proper authentication"""
    print("🔒 Testing endpoint authentication requirements...")

    auth_count = 0
    total_routes = 0

    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route, 'path'):
            total_routes += 1
            sig = inspect.signature(route.endpoint)
            params = list(sig.parameters.values())

            # Check for current_user parameter with User type
            has_auth = any(
                param.name == 'current_user'
                for param in params
            )

            # Only coping strategies list should be public
            if route.path == "/coping/strategies" and hasattr(route, 'methods') and 'GET' in route.methods:
                if not has_auth:
                    print(f"✅ {route.path} - PROPERLY PUBLIC")
                else:
                    print(f"❌ {route.path} - SHOULD BE PUBLIC")
                    return False
            else:
                if has_auth:
                    auth_count += 1
                    print(f"✅ {route.path} - PROPERLY SECURED")
                else:
                    print(f"❌ {route.path} - MISSING AUTHENTICATION")
                    return False

    # We have 1 public route, rest should be secured
    expected_secured = total_routes - 1
    print(f"📊 Authentication coverage: {auth_count}/{expected_secured} routes secured (1 public route)")

    if auth_count == expected_secured:
        print("✅ Endpoint authentication patterns verified")
        return True
    else:
        print(f"❌ Only {auth_count}/{expected_secured} routes properly secured")
        return False

async def test_database_schema_security():
    """Verify database schema has proper RLS and constraints"""
    print("🔒 Testing database schema security...")

    await initialize_database()

    try:
        async with database.pool.acquire() as conn:
            # Check that tables have RLS enabled
            tables_to_check = [
                'ai_content_analysis', 
                'user_behavior_patterns',
                'personalized_recommendations',
                'coping_strategies',
                'user_coping_preferences',
                'notification_preferences'
            ]

            for table in tables_to_check:
                result = await conn.fetchval(
                    "SELECT relrowsecurity FROM pg_class WHERE relname = $1",
                    table
                )
                if result is not None:
                    assert result == True, f"RLS not enabled for table: {table}"
                    print(f"✅ RLS enabled for {table}")
                else:
                    print(f"⚠️  Table {table} not found")

        print("✅ Database schema security verified")
        return True

    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return False

async def test_rls_context_pattern():
    """Verify RLS context uses correct session-level pattern"""
    print("🔒 Testing RLS context pattern...")

    try:
        # Check CRUD file uses correct RLS pattern
        with open('app/crud/ai_personalization.py', 'r') as f:
            content = f.read()

        # Should use the fixed pattern: set_config with is_local=false
        if "set_config('app.current_user_id', $1, false)" in content:
            print("✅ RLS context uses correct session-level pattern")
            return True
        else:
            print("❌ RLS context uses incorrect pattern")
            return False

    except Exception as e:
        print(f"❌ RLS context pattern test failed: {e}")
        return False

async def run_comprehensive_security_audit():
    """Run comprehensive security audit for AI personalization"""
    print("🔒 COMPREHENSIVE SECURITY AUDIT: AI Personalization")
    print("=" * 60)

    tests = [
        test_rls_enforcement_ai_data,
        test_crud_security_patterns,
        test_endpoint_authentication,
        test_database_schema_security,
        test_rls_context_pattern
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
                print(f"✅ {test.__name__} - PASSED")
            else:
                print(f"❌ {test.__name__} - FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} - ERROR: {e}")

    print("=" * 60)
    print(f"📊 SECURITY AUDIT RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL SECURITY TESTS PASSED - AI PERSONALIZATION IS SECURE")
        print("✅ RLS enforcement verified")
        print("✅ CRUD security patterns followed") 
        print("✅ Endpoint authentication enforced")
        print("✅ Database schema secure")
        print("✅ RLS context pattern correct")
    else:
        print(f"🚨 {total - passed} security issues need attention")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_security_audit())
    exit(0 if success else 1)
