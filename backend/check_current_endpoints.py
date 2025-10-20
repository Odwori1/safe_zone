#!/usr/bin/env python3
"""
Check current API endpoints structure
"""

import requests
import json

def check_current_endpoints():
    try:
        response = requests.get("http://localhost:8001/openapi.json")
        if response.status_code == 200:
            spec = response.json()
            
            print("📋 CURRENT API ENDPOINTS BY TAG:")
            print("=" * 50)
            
            # Group endpoints by tags
            endpoints_by_tag = {}
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    tags = details.get('tags', ['untagged'])
                    for tag in tags:
                        if tag not in endpoints_by_tag:
                            endpoints_by_tag[tag] = []
                        endpoints_by_tag[tag].append(f"{method.upper()} {path}")
            
            for tag, endpoints in sorted(endpoints_by_tag.items()):
                print(f"\n🏷️  {tag.upper()}:")
                for endpoint in sorted(endpoints):
                    print(f"   {endpoint}")
                    
            print(f"\n📊 Total endpoints: {sum(len(eps) for eps in endpoints_by_tag.values())}")
            print(f"📊 Total tags: {len(endpoints_by_tag)}")
            
        else:
            print("Cannot access OpenAPI spec")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_current_endpoints()
