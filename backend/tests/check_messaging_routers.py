#!/usr/bin/env python3
"""
CHECK WHAT MESSAGING ROUTERS EXIST
"""
import os
import importlib.util

def check_messaging_routers():
    """Check what messaging routers are available"""
    
    print("🔍 CHECKING MESSAGING ROUTERS")
    print("=" * 50)
    
    # Check endpoints directory for messaging files
    endpoints_dir = "app/api/endpoints"
    
    print("📁 ENDPOINT FILES:")
    for file in os.listdir(endpoints_dir):
        if file.endswith(".py") and file != "__init__.py":
            file_path = os.path.join(endpoints_dir, file)
            with open(file_path, "r") as f:
                content = f.read()
                
            # Check if it contains router definitions
            if "APIRouter" in content or "router =" in content:
                has_messaging = "message" in content.lower() or "conversation" in content.lower()
                status = "✅ MESSAGING" if has_messaging else "📄 OTHER"
                print(f"  {status} {file}")
                
                if has_messaging:
                    # Extract router prefix if any
                    import re
                    prefix_match = re.search(r'router\s*=\s*APIRouter\(.*?prefix=["\']([^"\']+)["\']', content, re.DOTALL)
                    if prefix_match:
                        print(f"        Prefix: {prefix_match.group(1)}")

def check_crud_implementation():
    """Check CRUD implementation for messaging"""
    
    print("\n📊 CRUD MESSAGING IMPLEMENTATION:")
    
    crud_files = [
        "app/crud/messages.py",
        "app/crud/conversations.py"  # Check if this exists
    ]
    
    for file_path in crud_files:
        exists = os.path.exists(file_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {status} {file_path}")
        
        if exists:
            with open(file_path, "r") as f:
                content = f.read()
                
            # Check for key methods
            methods = [
                "create_message", "get_messages", "create_conversation", 
                "get_conversation", "add_participant"
            ]
            
            found_methods = []
            for method in methods:
                if method in content:
                    found_methods.append(method)
                    
            if found_methods:
                print(f"        Methods: {', '.join(found_methods)}")

def check_schemas():
    """Check messaging schemas"""
    
    print("\n📋 MESSAGING SCHEMAS:")
    
    schema_files = [
        "app/schemas/messaging.py",
        "app/schemas/conversations.py"
    ]
    
    for file_path in schema_files:
        exists = os.path.exists(file_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {status} {file_path}")

if __name__ == "__main__":
    check_messaging_routers()
    check_crud_implementation()
    check_schemas()
