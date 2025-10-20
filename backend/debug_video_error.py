#!/usr/bin/env python3
"""
Debug the video posts error by making the request and checking server logs
"""
import requests
import json
import subprocess

def debug_video_error():
    print("🐛 DEBUGGING VIDEO POSTS ERROR")
    print("=" * 50)
    
    # Get authentication token
    login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
    response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("1. Testing video posts endpoint...")
    response = requests.get('http://localhost:8001/api/v1/posts/video?limit=10&skip=0', headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    print("\n2. Testing if the error is in a different endpoint...")
    # Test if the error happens in regular posts endpoint
    response = requests.get('http://localhost:8001/api/v1/posts/', headers=headers)
    print(f"   Regular posts status: {response.status_code}")
    
    # Test if the error happens with a specific post ID
    print("\n3. Testing single post retrieval...")
    # First get a post ID that exists
    response = requests.get('http://localhost:8001/api/v1/posts/', headers=headers)
    if response.status_code == 200 and len(response.json()) > 0:
        post_id = response.json()[0]['id']
        response = requests.get(f'http://localhost:8001/api/v1/posts/{post_id}', headers=headers)
        print(f"   Single post status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Single post error: {response.text}")
    else:
        print("   No posts available to test")
    
    print("\n4. The error message suggests it's in a 'get' method, not 'get_video_posts'")
    print("   This might be a method name conflict or wrong method being called!")

if __name__ == "__main__":
    debug_video_error()
