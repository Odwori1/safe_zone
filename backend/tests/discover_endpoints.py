#!/usr/bin/env python3
"""
DISCOVER AVAILABLE ENDPOINTS
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def discover_endpoints():
    """Discover all available API endpoints"""
    try:
        # Get OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            
            print("🔍 AVAILABLE MESSAGING ENDPOINTS:")
            print("=" * 50)
            
            for path, methods in schema.get('paths', {}).items():
                if '/messages/' in path or '/conversations' in path:
                    for method, details in methods.items():
                        print(f"{method.upper():>7} {path}")
                        if 'summary' in details:
                            print(f"         └─ {details['summary']}")
            
            print("\n🔍 AUTH ENDPOINTS:")
            print("=" * 50)
            for path, methods in schema.get('paths', {}).items():
                if 'auth' in path or 'register' in path or 'login' in path:
                    for method, details in methods.items():
                        print(f"{method.upper():>7} {path}")
            
            print("\n🔍 REGISTRATION SCHEMA:")
            print("=" * 50)
            # Find registration schema
            components = schema.get('components', {}).get('schemas', {})
            for schema_name, schema_def in components.items():
                if 'register' in schema_name.lower() or 'user' in schema_name.lower():
                    print(f"{schema_name}:")
                    if 'properties' in schema_def:
                        for prop, details in schema_def['properties'].items():
                            required = "REQUIRED" if prop in schema_def.get('required', []) else "optional"
                            print(f"  - {prop} ({required})")
            
    except Exception as e:
        print(f"Error discovering endpoints: {e}")

if __name__ == "__main__":
    discover_endpoints()
