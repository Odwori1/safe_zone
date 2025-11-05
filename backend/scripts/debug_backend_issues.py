#!/usr/bin/env python3
"""
Debug the actual backend issues causing 500 errors
"""

import requests
import json
import traceback

BASE_URL = "http://localhost:8001/api/v1"

def debug_backend_issues():
    # Login first
    login_data = {
        "email": "developer_test@example.com", 
        "password": "DeveloperPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return
        
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("🔧 DEBUGGING BACKEND 500 ERRORS")
    print("=" * 50)
    
    # Test 1: Moderation reports with detailed debugging
    print("\n1. 🛡️ TESTING MODERATION REPORTS ENDPOINT...")
    
    # First, let's get a real post ID to report
    response = requests.get(f"{BASE_URL}/posts", headers=headers)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            real_post_id = posts[0]['id']
            print(f"   Using real post ID: {real_post_id}")
            
            report_data = {
                "reported_content_type": "post",
                "reported_content_id": real_post_id,
                "report_reason": "inappropriate_content", 
                "description": "Test report debugging"
            }
        else:
            # Create a test post first
            post_data = {
                "content": "Test post for reporting",
                "mood": "calm",
                "visibility": "public",
                "is_anonymous": False
            }
            response = requests.post(f"{BASE_URL}/posts", json=post_data, headers=headers)
            if response.status_code == 200:
                real_post_id = response.json()['id']
                print(f"   Created test post with ID: {real_post_id}")
                
                report_data = {
                    "reported_content_type": "post",
                    "reported_content_id": real_post_id,
                    "report_reason": "inappropriate_content",
                    "description": "Test report debugging"
                }
            else:
                print("   ❌ Could not create test post")
                report_data = {
                    "reported_content_type": "post", 
                    "reported_content_id": "test-fake-id",
                    "report_reason": "inappropriate_content",
                    "description": "Test with fake ID"
                }
    else:
        print("   ❌ Could not fetch posts")
        report_data = {
            "reported_content_type": "post",
            "reported_content_id": "test-fake-id", 
            "report_reason": "inappropriate_content",
            "description": "Test with fake ID"
        }
    
    print(f"   Report data: {report_data}")
    response = requests.post(f"{BASE_URL}/moderation/reports", json=report_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # Test 2: Messaging system
    print("\n2. 💬 TESTING MESSAGING SYSTEM...")
    
    # First, check if we have conversations
    response = requests.get(f"{BASE_URL}/messages/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        print(f"   Found {len(conversations)} conversations")
        
        if conversations:
            conv_id = conversations[0]['id']
            print(f"   Testing with conversation: {conv_id}")
            
            message_data = {
                "content": "Test message for debugging",
                "message_type": "text"
            }
            
            response = requests.post(
                f"{BASE_URL}/messages/conversations/{conv_id}/messages",
                json=message_data, 
                headers=headers
            )
            print(f"   Message creation status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text}")
        else:
            # Try to create a conversation first
            print("   No conversations found, testing conversation creation...")
            
            # We need another user to create a conversation with
            # Let's see if we can find another user
            response = requests.get(f"{BASE_URL}/users/search?query=test", headers=headers)
            if response.status_code == 200:
                users = response.json()
                if users and len(users) > 1:  # More than just ourselves
                    other_user_id = users[1]['id']  # Get a different user
                    print(f"   Found user to message: {other_user_id}")
                    
                    conv_data = {
                        "participant_ids": [other_user_id],
                        "title": "Test Conversation"
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/messages/conversations",
                        json=conv_data,
                        headers=headers
                    )
                    print(f"   Conversation creation status: {response.status_code}")
                    if response.status_code == 200:
                        new_conv = response.json()
                        conv_id = new_conv['id']
                        
                        # Now test messaging
                        message_data = {
                            "content": "Test message after conversation creation",
                            "message_type": "text" 
                        }
                        
                        response = requests.post(
                            f"{BASE_URL}/messages/conversations/{conv_id}/messages",
                            json=message_data,
                            headers=headers
                        )
                        print(f"   Message creation status: {response.status_code}")
                        if response.status_code != 200:
                            print(f"   Error: {response.text}")
    
    print("\n🔍 SUMMARY OF ISSUES:")
    print("   If you see 500 errors, check:")
    print("   1. Backend logs for stack traces")
    print("   2. Database table permissions") 
    print("   3. Foreign key relationships")
    print("   4. RLS policies blocking operations")

if __name__ == "__main__":
    debug_backend_issues()
