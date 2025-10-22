#!/usr/bin/env python3
"""
COMPREHENSIVE SECURITY AUDIT - Phase 1 to Phase 3
"""
import subprocess
import sys

def run_security_test(test_file, description):
    """Run a security test and report results"""
    print(f"\n🔍 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ PASS")
            return True
        else:
            print("❌ FAIL")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"🚨 ERROR: {e}")
        return False

def main():
    print("🎯 COMPREHENSIVE SECURITY AUDIT - SAFE ZONE")
    print("=" * 60)
    
    # Test files to run (adjust paths as needed)
    test_suite = [
        # Phase 1: Foundation
        ("tests/test_auth_system.py", "Authentication System"),
        ("tests/test_security_foundation.py", "Security Foundation"),
        ("tests/test_rate_limiting.py", "Rate Limiting"),
        
        # Phase 2: Core Features  
        ("tests/test_posts_fixed.py", "Posts RLS Enforcement"),
        ("tests/test_comments_system.py", "Comments Isolation"),
        ("tests/test_journals_system.py", "Journals Privacy"),
        ("tests/test_mood_system.py", "Mood Tracking"),
        ("tests/test_crisis_system_final.py", "Crisis System"),
        
        # Phase 3: Current
        ("tests/test_secure_s3_implementation.py", "S3 Security"),
        ("tests/test_websocket_infrastructure_fixed.py", "WebSocket Security"),
        ("tests/test_messages_crud_fixed.py", "Messaging CRUD")
    ]
    
    results = []
    
    for test_file, description in test_suite:
        passed = run_security_test(test_file, description)
        results.append((description, passed))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SECURITY AUDIT SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"Tests Passed: {passed_count}/{total_count}")
    print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
    
    print("\n🔍 DETAILED RESULTS:")
    for description, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {description}")
    
    # Overall assessment
    if passed_count == total_count:
        print("\n🎉 EXCELLENT: All security tests passed!")
        print("   Application is secure and ready for production.")
    elif passed_count >= total_count * 0.8:
        print("\n⚠️  GOOD: Most security tests passed.")
        print("   Review failed tests before production.")
    else:
        print("\n🚨 CRITICAL: Multiple security failures.")
        print("   Address security issues before proceeding.")

if __name__ == "__main__":
    main()
