#!/usr/bin/env python3
"""
Verify audio endpoints are registered and working
"""

import requests
import json

def verify_audio_endpoints():
    print("🔍 VERIFYING AUDIO ENDPOINTS REGISTRATION")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8001/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            
            # Check for uploads tag
            tags = [tag['name'] for tag in spec.get('tags', [])]
            if 'uploads' in tags:
                print("✅ Uploads tag registered")
            else:
                print("❌ Uploads tag not found")
            
            # Check for audio endpoints
            audio_endpoints = []
            for path, methods in spec['paths'].items():
                if 'audio' in path or 'upload' in path:
                    for method in methods:
                        endpoint_info = f"{method.upper()} {path}"
                        audio_endpoints.append(endpoint_info)
            
            if audio_endpoints:
                print("✅ Audio endpoints registered:")
                for endpoint in sorted(audio_endpoints):
                    print(f"   {endpoint}")
            else:
                print("❌ No audio endpoints found")
            
            # Check posts endpoints for audio support
            posts_with_audio = []
            for path, methods in spec['paths'].items():
                if 'posts' in path:
                    for method, details in methods.items():
                        if 'audio' in str(details).lower():
                            posts_with_audio.append(f"{method.upper()} {path}")
            
            if posts_with_audio:
                print("✅ Posts endpoints with audio support:")
                for endpoint in sorted(posts_with_audio):
                    print(f"   {endpoint}")
            
            print(f"\n📊 Total endpoints: {len(spec['paths'])}")
            print(f"📊 Total tags: {len(tags)}")
            
        else:
            print("Cannot access OpenAPI spec")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_audio_endpoints()
