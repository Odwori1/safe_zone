#!/usr/bin/env python3
"""
Check backend logs and status
"""

import subprocess
import time
import requests

def check_backend_status():
    print("🔍 CHECKING BACKEND STATUS AND LOGS")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8001/api/v1/health", timeout=5)
        print(f"✅ Backend is running - Status: {response.status_code}")
    except:
        print("❌ Backend is not running or not accessible")
        return
    
    # Check recent logs (if available)
    print("\n📋 RECENT LOGS (if available):")
    try:
        # Try to get recent logs from the backend process
        result = subprocess.run(
            ["journalctl", "-u", "safe_zone_backend", "--since", "5 minutes ago", "--no-pager"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:  # Last 10 lines
                if 'ERROR' in line or '500' in line:
                    print(f"   🔴 {line}")
                elif 'WARNING' in line:
                    print(f"   🟡 {line}")
        else:
            print("   No systemd service logs found")
    except:
        print("   Could not access system logs")
    
    # Check for application logs
    try:
        import os
        log_path = "logs/app.log"
        if os.path.exists(log_path):
            print(f"\n📄 APPLICATION LOGS ({log_path}):")
            with open(log_path, 'r') as f:
                lines = f.readlines()[-20:]  # Last 20 lines
                for line in lines:
                    if 'ERROR' in line or 'Exception' in line:
                        print(f"   🔴 {line.strip()}")
        else:
            print(f"\n📄 No application log file found at {log_path}")
    except Exception as e:
        print(f"   Could not read application logs: {e}")

if __name__ == "__main__":
    check_backend_status()
