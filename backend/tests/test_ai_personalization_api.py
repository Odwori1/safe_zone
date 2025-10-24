"""
Test AI personalization API endpoints
"""

import asyncio
from app.database.database import database
from app.api.endpoints.ai_personalization import router

async def test_api_endpoints():
    """Test API endpoint structure and security"""
    print("🧪 TESTING AI PERSONALIZATION API ENDPOINTS")
    print("=" * 50)
    
    # Test 1: Check router endpoints exist
    endpoints = [
        ("GET", "/content/{content_type}/{content_id}/analysis"),
        ("GET", "/behavior/patterns"),
        ("GET", "/recommendations"),
        ("POST", "/recommendations/{recommendation_id}/interact"),
        ("GET", "/coping/strategies"),
        ("GET", "/coping/preferences"),
        ("POST", "/coping/strategies/{strategy_id}/preference"),
        ("GET", "/notifications/preferences"),
        ("PUT", "/notifications/preferences"),
        ("GET", "/health")
    ]
    
    found_endpoints = []
    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                found_endpoints.append((method, route.path))
    
    print(f"✅ Found {len(found_endpoints)} endpoints")
    
    # Check if all expected endpoints exist
    missing_endpoints = []
    for method, path in endpoints:
        if (method, path) not in found_endpoints:
            missing_endpoints.append((method, path))
    
    if not missing_endpoints:
        print("✅ All expected endpoints are registered")
    else:
        print(f"❌ Missing endpoints: {missing_endpoints}")
        return False
    
    # Test 2: Check endpoint security
    import inspect
    auth_count = 0
    total_routes = len(found_endpoints)
    
    for method, path in found_endpoints:
        # Find the route object
        route = None
        for r in router.routes:
            if hasattr(r, 'path') and r.path == path and method in getattr(r, 'methods', []):
                route = r
                break
        
        if route and hasattr(route, 'endpoint'):
            sig = inspect.signature(route.endpoint)
            params = list(sig.parameters.values())
            
            # Check for current_user parameter (indicates authentication)
            has_auth = any(param.name == 'current_user' for param in params)
            
            # Only coping strategies list should be public
            if path == "/coping/strategies" and method == "GET":
                if not has_auth:
                    print(f"✅ {method} {path} - PUBLIC (correct)")
                else:
                    print(f"❌ {method} {path} - SHOULD BE PUBLIC")
                    return False
            else:
                # All other endpoints should require authentication
                if has_auth:
                    auth_count += 1
                    print(f"✅ {method} {path} - SECURED")
                else:
                    print(f"❌ {method} {path} - MISSING AUTHENTICATION")
                    return False
    
    # We have 1 public route (coping strategies) and the rest should be secured
    expected_secured_routes = total_routes - 1
    print(f"📊 Authentication coverage: {auth_count}/{expected_secured_routes} routes secured (1 public route)")
    
    if auth_count == expected_secured_routes:
        print("✅ All endpoints properly secured")
    else:
        print(f"❌ Security configuration incorrect")
        return False
    
    print("🎉 ALL API ENDPOINT TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_api_endpoints())
    exit(0 if success else 1)
