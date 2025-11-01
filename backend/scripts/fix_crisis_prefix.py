#!/usr/bin/env python3
"""
Fix the crisis router prefix in main.py
"""
import os

def fix_crisis_prefix():
    """Fix the duplicate crisis router includes"""
    
    main_py_path = os.path.expanduser("~/safe_zone/backend/app/main.py")
    
    print(f"📝 Fixing crisis router prefix in {main_py_path}...")
    
    # Read the current main.py
    with open(main_py_path, 'r') as f:
        lines = f.readlines()
    
    # Find and remove the duplicate crisis router includes
    crisis_lines = []
    for i, line in enumerate(lines):
        if "crisis.router" in line:
            crisis_lines.append(i)
    
    print(f"🔍 Found {len(crisis_lines)} crisis router includes:")
    for line_num in crisis_lines:
        print(f"   Line {line_num+1}: {lines[line_num].strip()}")
    
    # Keep only the first one and fix its prefix
    if len(crisis_lines) >= 2:
        # Remove the second one (line 49)
        lines.pop(crisis_lines[1])
        print("✅ Removed duplicate crisis router include")
    
    # Fix the first one to use the correct prefix
    if crisis_lines:
        first_line_num = crisis_lines[0]
        old_line = lines[first_line_num]
        # Change prefix from "/api/v1/crisis" to "/api/v1/crisis-support"
        new_line = old_line.replace('prefix="/api/v1/crisis"', 'prefix="/api/v1/crisis-support"')
        lines[first_line_num] = new_line
        print("✅ Updated crisis router prefix to '/api/v1/crisis-support'")
    
    # Write the updated file
    with open(main_py_path, 'w') as f:
        f.writelines(lines)
    
    print("🎉 Crisis router prefix fixed!")
    print("\n📋 Crisis endpoints will now be available at:")
    print("   /api/v1/crisis-support/resources/")
    print("   /api/v1/crisis-support/emergency-contacts/")
    print("   /api/v1/crisis-support/safety-plans/")
    print("   /api/v1/crisis-support/wellness-checkins/")
    print("   /api/v1/crisis-support/crisis-alerts/")
    print("   /api/v1/crisis-support/preferences/")

if __name__ == "__main__":
    fix_crisis_prefix()
