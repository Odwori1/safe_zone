#!/usr/bin/env python3
"""
Quick diagnostic for audio implementation status
"""
import os
import sys

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        print(f"✅ {description}: EXISTS")
        return True
    else:
        print(f"❌ {description}: MISSING")
        return False

def check_file_contains(filepath, pattern, description):
    if not os.path.exists(filepath):
        print(f"❌ {description}: FILE MISSING")
        return False
        
    with open(filepath, 'r') as f:
        content = f.read()
        if pattern in content:
            print(f"✅ {description}: FOUND")
            return True
        else:
            print(f"❌ {description}: NOT FOUND")
            return False

print("🔍 QUICK AUDIO IMPLEMENTATION DIAGNOSTIC")
print("=" * 40)

# Check critical files
files_to_check = [
    ("~/safe_zone/backend/app/main.py", "Main application file"),
    ("~/safe_zone/backend/app/schemas/post.py", "Post schemas"),
    ("~/safe_zone/backend/app/api/endpoints/uploads.py", "Uploads endpoints"),
    ("~/safe_zone/backend/app/core/storage.py", "Storage configuration"),
    ("~/safe_zone/backend/app/crud/post.py", "Post CRUD operations"),
]

for filepath, description in files_to_check:
    expanded_path = os.path.expanduser(filepath)
    check_file_exists(expanded_path, description)

print("\n🔍 Checking for audio-specific patterns...")
patterns_to_check = [
    ("~/safe_zone/backend/app/main.py", "uploads", "Uploads router registration"),
    ("~/safe_zone/backend/app/schemas/post.py", "audio", "Audio schema definitions"),
    ("~/safe_zone/backend/app/api/endpoints/posts.py", "audio", "Audio endpoints in posts"),
    ("~/safe_zone/backend/app/crud/post.py", "audio", "Audio CRUD methods"),
]

for filepath, pattern, description in patterns_to_check:
    expanded_path = os.path.expanduser(filepath)
    check_file_contains(expanded_path, pattern, description)

print("\n🎯 SUMMARY:")
print("Run the comprehensive test for detailed analysis:")
print("python3 test_audio_comprehensive.py")
