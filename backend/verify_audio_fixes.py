#!/usr/bin/env python3
"""
Complete verification of audio implementation fixes
"""
import sys
import os

def verify_all_fixes():
    print("🎵 COMPREHENSIVE AUDIO FIXES VERIFICATION")
    print("=" * 50)
    
    checks_passed = 0
    checks_failed = 0
    
    # Check 1: Main.py imports
    print("1. Checking main.py imports...")
    try:
        with open('app/main.py', 'r') as f:
            main_content = f.read()
            
        if 'from app.api.endpoints import' in main_content and 'uploads' in main_content:
            print("   ✅ uploads imported in main.py")
            checks_passed += 1
        else:
            print("   ❌ uploads NOT imported in main.py")
            checks_failed += 1
            
        if 'app.include_router(uploads.router' in main_content:
            print("   ✅ uploads router registered in main.py")
            checks_passed += 1
        else:
            print("   ❌ uploads router NOT registered in main.py")
            checks_failed += 1
    except Exception as e:
        print(f"   ❌ Error checking main.py: {e}")
        checks_failed += 1
    
    # Check 2: Uploads.py schema imports
    print("2. Checking uploads.py schema imports...")
    try:
        with open('app/api/endpoints/uploads.py', 'r') as f:
            uploads_content = f.read()
            
        if 'from app.schemas.post import' in uploads_content:
            print("   ✅ uploads.py imports from app.schemas.post")
            checks_passed += 1
        else:
            print("   ❌ uploads.py has wrong schema imports")
            checks_failed += 1
    except Exception as e:
        print(f"   ❌ Error checking uploads.py: {e}")
        checks_failed += 1
    
    # Check 3: Test server imports
    print("3. Testing server startup...")
    try:
        from app.main import app
        print("   ✅ Server imports successfully")
        checks_passed += 1
        
        # Check routes
        upload_routes = [route for route in app.routes if hasattr(route, 'path') and '/uploads' in getattr(route, 'path', '')]
        if upload_routes:
            print(f"   ✅ Found {len(upload_routes)} upload routes")
            checks_passed += 1
        else:
            print("   ❌ No upload routes found")
            checks_failed += 1
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        checks_failed += 1
    except Exception as e:
        print(f"   ❌ Other error: {e}")
        checks_failed += 1
    
    # Check 4: Check if posts_audio.py duplicate exists
    print("4. Checking for duplicate files...")
    try:
        if os.path.exists('app/api/endpoints/posts_audio.py'):
            print("   ❌ posts_audio.py duplicate exists - should be removed")
            checks_failed += 1
        else:
            print("   ✅ No posts_audio.py duplicate")
            checks_passed += 1
    except Exception as e:
        print(f"   ❌ Error checking duplicates: {e}")
        checks_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION SUMMARY:")
    print(f"   ✅ Passed: {checks_passed}")
    print(f"   ❌ Failed: {checks_failed}")
    print(f"   📈 Success Rate: {checks_passed/(checks_passed+checks_failed)*100:.1f}%")
    
    if checks_failed == 0:
        print("\n🎉 ALL CHECKS PASSED! Audio implementation should work.")
        print("   Run: python3 test_audio_comprehensive.py")
    else:
        print(f"\n⚠️  {checks_failed} checks failed. Please fix these issues.")
        
    return checks_failed == 0

if __name__ == "__main__":
    success = verify_all_fixes()
    sys.exit(0 if success else 1)
