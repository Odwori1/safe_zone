#!/usr/bin/env python3
"""
Fix crisis routes registration in main.py
"""
import os

def fix_main_py():
    """Add crisis router to main.py if missing"""
    
    main_py_path = os.path.expanduser("~/safe_zone/backend/app/main.py")
    
    # Read the current main.py
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    # Check if crisis router is already included
    if "crisis.router" in content:
        print("✅ Crisis router already registered in main.py")
        return
    
    # Find where to add the crisis router
    if "app.include_router" in content:
        # Find the last app.include_router line
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if "app.include_router" in line and "tags=" in line:
                insert_index = i + 1
        
        if insert_index is not None:
            # Add the crisis router import if missing
            if "from app.api.endpoints import crisis" not in content:
                # Find where to add the import
                import_lines = []
                for i, line in enumerate(lines):
                    if "from app.api.endpoints import" in line and "crisis" not in line:
                        import_lines.append(i)
                
                if import_lines:
                    last_import_line = max(import_lines)
                    lines.insert(last_import_line + 1, "from app.api.endpoints import crisis")
            
            # Add the crisis router
            lines.insert(insert_index, 'app.include_router(crisis.router, prefix="/api/v1", tags=["crisis-support"])')
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Added crisis router to main.py")
            print("🔧 Changes made:")
            print("   - Added import: from app.api.endpoints import crisis")
            print('   - Added route: app.include_router(crisis.router, prefix="/api/v1", tags=["crisis-support"])')
        else:
            print("❌ Could not find where to insert crisis router")
    else:
        print("❌ No app.include_router lines found in main.py")

if __name__ == "__main__":
    fix_main_py()
