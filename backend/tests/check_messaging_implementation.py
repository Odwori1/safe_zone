#!/usr/bin/env python3
"""
CHECK WHAT MESSAGING CODE ACTUALLY EXISTS
"""
import os
import importlib.util

def check_messaging_files():
    """Check what messaging-related files exist"""
    
    print("🔍 CHECKING MESSAGING IMPLEMENTATION FILES")
    print("=" * 60)
    
    base_path = "app"
    
    # Files that should exist for messaging (from handover report)
    expected_files = [
        "api/endpoints/websocket.py",
        "api/endpoints/messages.py",  # This might be missing!
        "crud/messages.py", 
        "schemas/messaging.py",
        "services/websocket_auth.py",
        "services/connection_manager_enhanced.py",
        "services/redis_service.py",
        "services/realtime_features.py"
    ]
    
    print("📁 EXPECTED MESSAGING FILES:")
    for file_path in expected_files:
        full_path = os.path.join(base_path, file_path)
        exists = os.path.exists(full_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {status} {file_path}")
        
        if exists:
            # Check file size
            size = os.path.getsize(full_path)
            print(f"       Size: {size} bytes")
            
            # Check if it's not empty
            if size > 100:
                print(f"       📝 Has content")
            else:
                print(f"       ⚠️  Very small file")

def check_websocket_endpoint():
    """Check if WebSocket endpoint is registered"""
    print("\n🔌 CHECKING WEBSOCKET ENDPOINT:")
    
    try:
        # Try to import and check websocket router
        spec = importlib.util.spec_from_file_location("websocket", "app/api/endpoints/websocket.py")
        if spec:
            websocket_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(websocket_module)
            
            if hasattr(websocket_module, 'router'):
                print("✅ WebSocket router exists")
                # Check if it has the expected endpoint
                print("   WebSocket endpoint should be at: /ws")
            else:
                print("❌ No router in websocket.py")
        else:
            print("❌ Cannot import websocket module")
    except Exception as e:
        print(f"❌ Error checking websocket: {e}")

def check_main_app_setup():
    """Check if WebSocket is included in main app"""
    print("\n🏗️ CHECKING MAIN APP SETUP:")
    
    try:
        with open("main.py", "r") as f:
            content = f.read()
            
        if "websocket" in content.lower() or "WebSocket" in content:
            print("✅ WebSocket mentioned in main.py")
        else:
            print("❌ WebSocket not found in main.py")
            
        if "include_router" in content and "websocket" in content:
            print("✅ WebSocket router included in app")
        else:
            print("❌ WebSocket router may not be included")
            
    except Exception as e:
        print(f"Error reading main.py: {e}")

if __name__ == "__main__":
    check_messaging_files()
    check_websocket_endpoint() 
    check_main_app_setup()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("If messaging endpoints are missing but files exist, the feature")
    print("may be implemented but not exposed via REST API (WebSocket only).")
    print("The RLS issue is confirmed - policies exist but are bypassed.")
