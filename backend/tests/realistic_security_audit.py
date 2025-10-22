#!/usr/bin/env python3
"""
REALISTIC SECURITY AUDIT - Based on actual existing tests
"""
import subprocess
import sys
import os

def get_existing_tests():
    """Get list of actual test files that exist"""
    test_files = []
    for file in os.listdir("tests"):
        if file.endswith(".py") and file.startswith(("test_", "security_", "audit")):
            test_files.append(file)
    return sorted(test_files)

def run_test(test_file):
    """Run a single test file"""
    test_path = f"tests/{test_file}"
    
    print(f"\n🔍 {test_file}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ PASS")
            # Show key success indicators
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if any(keyword in line for keyword in ['✅', 'PASS', 'SUCCESS', 'WORKING']):
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ FAIL")
            # Show key error information
            error_lines = result.stderr.split('\n')
            for line in error_lines[-5:]:  # Last 5 lines of error
                if line.strip():
                    print(f"   {line.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"🚨 ERROR: {e}")
        return False

def main():
    print("🎯 REALISTIC SECURITY AUDIT - ACTUAL TESTS")
    print("=" * 60)
    
    # Get actual test files
    test_files = get_existing_tests()
    print(f"Found {len(test_files)} test files:")
    
    for test_file in test_files:
        print(f"  📄 {test_file}")
    
    # Run tests
    results = []
    for test_file in test_files:
        passed = run_test(test_file)
        results.append((test_file, passed))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REALISTIC AUDIT SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"Tests Passed: {passed_count}/{total_count}")
    print(f"Success Rate: {(passed_count/total_count)*100:.1f}%" if total_count > 0 else "N/A")
    
    print("\n🔍 DETAILED RESULTS:")
    for test_file, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_file}")

if __name__ == "__main__":
    main()
