#!/usr/bin/env python3
"""
Fix main.py to include crisis router
"""
import os

def fix_main_py():
    """Add crisis router to main.py"""
    
    main_py_path = os.path.expanduser("~/safe_zone/backend/app/main.py")
    
    print(f"📝 Editing {main_py_path}...")
    
    # Read the current main.py
    with open(main_py_path, 'r') as f:
        lines = f.readlines()
    
    # Check if crisis is already imported and registered
    crisis_imported = any("from app.api.endpoints import crisis" in line for line in lines)
    crisis_registered = any("crisis.router" in line for line in lines)
    
    if crisis_imported and crisis_registered:
        print("✅ Crisis router already imported and registered")
        return
    
    # Find the import section and add crisis import
    if not crisis_imported:
        print("🔧 Adding crisis import...")
        # Find where to add the import (after other endpoint imports)
        import_index = None
        for i, line in enumerate(lines):
            if "from app.api.endpoints import" in line:
                import_index = i
        
        if import_index is not None:
            lines.insert(import_index + 1, "from app.api.endpoints import crisis\n")
            print("✅ Added crisis import")
        else:
            print("❌ Could not find where to add crisis import")
            return
    
    # Find where to add the crisis router registration
    if not crisis_registered:
        print("🔧 Adding crisis router registration...")
        # Find the last app.include_router line
        router_index = None
        for i, line in enumerate(lines):
            if "app.include_router" in line and "tags=" in line:
                router_index = i
        
        if router_index is not None:
            # Add crisis router after the last router
            lines.insert(router_index + 1, 'app.include_router(crisis.router, prefix="/api/v1", tags=["crisis-support"])\n')
            print("✅ Added crisis router registration")
        else:
            print("❌ Could not find where to add crisis router")
            return
    
    # Write the updated file
    with open(main_py_path, 'w') as f:
        f.writelines(lines)
    
    print("🎉 main.py updated successfully!")
    
    # Show the changes
    print("\n📋 Changes made:")
    for i, line in enumerate(lines):
        if "crisis" in line:
            print(f"   Line {i+1}: {line.strip()}")

if __name__ == "__main__":
    fix_main_py()
