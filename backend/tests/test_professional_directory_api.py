"""
Test professional directory API endpoints
"""

import asyncio
from app.database.database import database
from app.api.endpoints.professional_directory import router

async def test_api_endpoints():
    """Test API endpoint structure and security"""
    print("🧪 TESTING PROFESSIONAL DIRECTORY API ENDPOINTS")
    print("=" * 50)
    
    # Test 1: Check router endpoints exist
    endpoints = [
        ("POST", "/profiles"),
        ("GET", "/profiles/me"), 
        ("PUT", "/profiles/me"),
        ("GET", "/profiles/{user_id}"),
        ("GET", "/directory"),
        ("POST", "/directory/search"),
        ("POST", "/verifications"),
        ("GET", "/verifications/me"),
        ("POST", "/availability"),
        ("GET", "/availability/{professional_id}"),
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
    
    # Test 2: Check endpoint security (all should require authentication)
    import inspect
    auth_count = 0
    total_routes = 0
    
    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route, 'path'):
            total_routes += 1
            sig = inspect.signature(route.endpoint)
            params = list(sig.parameters.values())
            
            # Check for current_user parameter (indicates authentication)
            has_auth = any(
                param.name == 'current_user'
                for param in params
            )
            
            if has_auth:
                auth_count += 1
                print(f"✅ {route.path} - SECURED")
            else:
                print(f"❌ {route.path} - MISSING AUTHENTICATION")
    
    print(f"📊 Authentication coverage: {auth_count}/{total_routes} routes")
    
    if auth_count == total_routes:
        print("✅ All endpoints require authentication")
    else:
        print(f"❌ Only {auth_count}/{total_routes} routes require authentication")
        return False
    
    print("🎉 ALL API ENDPOINT TESTS PASSED!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_api_endpoints())
    exit(0 if success else 1)
