#!/usr/bin/env python3
"""
Find specific audio implementation issues
"""
import os
import re

def analyze_file(filepath, issues):
    if not os.path.exists(filepath):
        issues.append(f"❌ File missing: {filepath}")
        return
        
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        
    filename = os.path.basename(filepath)
    
    if filename == "main.py":
        # Check for uploads router registration
        if "uploads" not in content and "include_router" in content:
            issues.append("❌ main.py: Uploads router not registered")
        
        # Count router registrations
        router_count = content.count("include_router")
        issues.append(f"ℹ️ main.py: {router_count} routers registered")
        
    elif filename == "post.py" and "schemas" in filepath:
        # Check for audio schemas
        audio_schemas = ['AudioPostCreate', 'AudioPostResponse']
        for schema in audio_schemas:
            if schema in content:
                issues.append(f"✅ schemas/post.py: {schema} found")
            else:
                issues.append(f"❌ schemas/post.py: {schema} missing")
                
    elif filename == "uploads.py":
        # Check if uploads endpoint has audio support
        if "audio" in content.lower():
            issues.append("✅ uploads.py: Audio support found")
        else:
            issues.append("❌ uploads.py: Audio support missing")
            
    elif filename == "storage.py":
        if "upload_audio_file" in content:
            issues.append("✅ storage.py: upload_audio_file function exists")
        else:
            issues.append("❌ storage.py: upload_audio_file function missing")

print("🔍 ANALYZING AUDIO IMPLEMENTATION ISSUES")
print("=" * 50)

issues = []

# Analyze critical files
files_to_analyze = [
    "~/safe_zone/backend/app/main.py",
    "~/safe_zone/backend/app/schemas/post.py", 
    "~/safe_zone/backend/app/api/endpoints/uploads.py",
    "~/safe_zone/backend/app/core/storage.py",
    "~/safe_zone/backend/app/crud/post.py",
]

for filepath in files_to_analyze:
    expanded_path = os.path.expanduser(filepath)
    analyze_file(expanded_path, issues)

print("\n".join(issues))

print("\n🎯 PRIORITY FIXES:")
print("1. Fix router registration in main.py")
print("2. Ensure audio schemas are in post.py (not post_audio.py)")
print("3. Implement upload_audio_file in storage.py")
print("4. Complete uploads endpoints with audio support")
print("5. Add audio CRUD methods in crud/post.py")
