#!/usr/bin/env python3
"""
Test if crisis router is properly set up
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.api.endpoints import crisis
    from app.main import app
    
    print("✅ Crisis router imported successfully")
    
    # Check if crisis routes are registered
    crisis_routes = [route for route in app.routes if hasattr(route, 'path') and '/crisis-support' in route.path]
    
    if crisis_routes:
        print(f"✅ Found {len(crisis_routes)} crisis support routes:")
        for route in crisis_routes:
            methods = getattr(route, 'methods', ['ANY'])
            print(f"   {', '.join(methods):<10} {route.path}")
    else:
        print("❌ No crisis support routes found in app")
        
except ImportError as e:
    print(f"❌ Failed to import crisis router: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
