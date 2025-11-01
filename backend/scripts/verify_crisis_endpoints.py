#!/usr/bin/env python3
"""
Verify and fix crisis endpoints file
"""
import os

def verify_crisis_endpoints():
    """Verify crisis endpoints file has proper router setup"""
    
    crisis_py_path = os.path.expanduser("~/safe_zone/backend/app/api/endpoints/crisis.py")
    
    print(f"🔍 Checking {crisis_py_path}...")
    
    # Read the current file
    with open(crisis_py_path, 'r') as f:
        content = f.read()
    
    # Check if router is defined
    if "router = APIRouter()" not in content:
        print("❌ Router not defined in crisis endpoints")
        
        # Find where to add the router (after imports)
        lines = content.split('\n')
        insert_index = None
        
        for i, line in enumerate(lines):
            if "from app.crud.crisis import crisis_crud" in line:
                insert_index = i + 1
                break
        
        if insert_index is not None:
            lines.insert(insert_index, "")
            lines.insert(insert_index + 1, "# Create the router")
            lines.insert(insert_index + 2, "router = APIRouter()")
            lines.insert(insert_index + 3, "")
            
            # Write the updated file
            with open(crisis_py_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Added router definition to crisis endpoints")
        else:
            print("❌ Could not find where to add router")
    else:
        print("✅ Router is properly defined in crisis endpoints")
    
    # Check if file ends properly
    if not content.strip().endswith(')'):
        print("⚠️  File might not end properly, checking...")
        # Add a closing parenthesis if needed
        if content.strip().endswith('"""'):
            with open(crisis_py_path, 'a') as f:
                f.write('\n')
            print("✅ Added newline to end of file")

if __name__ == "__main__":
    verify_crisis_endpoints()
