"""
ACCURATE SECURITY VERIFICATION - Enhanced Moderation
Properly checks that authentication is implemented
"""
import inspect
from app.api.endpoints.enhanced_moderation import router

def verify_endpoint_authentication_accurate():
    """Accurately verify all endpoints require authentication"""
    print("🔒 ACCURATE ENDPOINT AUTHENTICATION VERIFICATION")
    print("=" * 50)
    
    auth_count = 0
    total_routes = 0
    
    for route in router.routes:
        if hasattr(route, 'endpoint') and hasattr(route, 'path'):
            total_routes += 1
            sig = inspect.signature(route.endpoint)
            params = list(sig.parameters.values())
            
            # Check for current_user parameter with User type
            has_auth = any(
                param.name == 'current_user' and 
                hasattr(param.annotation, '__name__') and 
                param.annotation.__name__ == 'User'
                for param in params
            )
            
            if has_auth:
                auth_count += 1
                print(f"✅ {route.path} - PROPERLY SECURED")
            else:
                print(f"❌ {route.path} - MISSING AUTHENTICATION")
    
    print("=" * 50)
    print(f"📊 AUTHENTICATION RESULTS: {auth_count}/{total_routes} endpoints secured")
    
    if auth_count == total_routes:
        print("🎉 ALL ENDPOINTS PROPERLY SECURED WITH AUTHENTICATION!")
        return True
    else:
        print(f"🚨 {total_routes - auth_count} ENDPOINTS MISSING AUTHENTICATION!")
        return False

if __name__ == "__main__":
    success = verify_endpoint_authentication_accurate()
    exit(0 if success else 1)
