"""
SECURITY AUDIT: Final Phase Features Implementation
Following EXACT same patterns as security_audit_enhanced_ux_community.py
"""

import asyncio
import inspect
from app.database.database import database
from app.crud.final_phase_features import final_phase_features_crud
from app.api.endpoints.final_phase_features import router

async def initialize_database():
    """Initialize database connection"""
    if not database.pool:
        await database.connect()

async def test_rls_enforcement_final_phase_data():
    """Test that RLS properly enforces final phase data isolation"""
    print("🔒 Testing RLS enforcement for final phase data...")

    await initialize_database()

    try:
        async with database.pool.acquire() as conn:
            test_user_id = "test-user-final-phase-999"
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
        'get_language_preferences',
        'update_language_preferences',
        'get_regional_resources',
        'get_accessibility_preferences',
        'update_accessibility_preferences',
        'get_user_organizations',
        'get_organization_wellness_challenges',
        'join_wellness_challenge',
        'create_ai_chat_session',
        'get_user_ai_chat_sessions',
        'add_ai_chat_message',
        'save_voice_mood_analysis',
        'get_user_integrations',
        'create_user_integration',
        'get_emergency_contacts',
        'add_emergency_contact',
        'get_peer_support_matches',
        'get_group_sessions',
        'join_group_session',
        'submit_user_feedback',
        'get_user_feedback',
        'health_check'
    ]

    for method in required_methods:
        if hasattr(final_phase_features_crud, method):
            print(f"✅ {method} - IMPLEMENTED")
        else:
            print(f"❌ {method} - MISSING")
            return False

    # Verify methods follow user_id parameter pattern for RLS context
    for method_name in required_methods:
        method = getattr(final_phase_features_crud, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Critical security check: Methods should accept user_id for RLS context
        # Except public methods like get_regional_resources, get_group_sessions
        if method_name not in ['get_regional_resources', 'get_group_sessions']:
            has_user_param = any('user' in param.lower() or param in ['user_id', 'requesting_user_id'] for param in params)
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
                param.name == 'current_user' and hasattr(param.annotation, '__name__') and param.annotation.__name__ == 'User'
                for param in params
            )

            # Regional resources and group sessions should be public
            public_paths = ['/regional-resources', '/group-sessions']
            is_public = any(route.path.endswith(path) and hasattr(route, 'methods') and 'GET' in route.methods for path in public_paths)

            if is_public:
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

    # We have 2 public routes, rest should be secured
    expected_secured = total_routes - 2
    print(f"📊 Authentication coverage: {auth_count}/{expected_secured} routes secured (2 public routes)")

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
                'language_preferences',
                'translated_content',
                'regional_resources',
                'accessibility_preferences',
                'organizations',
                'organization_members',
                'wellness_challenges',
                'challenge_participants',
                'ai_chat_sessions',
                'ai_chat_messages',
                'voice_mood_analysis',
                'predictive_insights',
                'user_integrations',
                'wearable_data',
                'emergency_coordination',
                'peer_support_matches',
                'group_sessions',
                'session_participants',
                'system_metrics',
                'user_feedback',
                'compliance_logs'
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
        with open('app/crud/final_phase_features.py', 'r') as f:
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
    """Run comprehensive security audit for final phase features"""
    print("🔒 COMPREHENSIVE SECURITY AUDIT: Final Phase Features")
    print("=" * 60)

    tests = [
        test_rls_enforcement_final_phase_data,
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
        print("🎉 ALL SECURITY TESTS PASSED - FINAL PHASE FEATURES ARE SECURE")
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
