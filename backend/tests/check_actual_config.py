#!/usr/bin/env python3
"""
CHECK ACTUAL DATABASE CONFIGURATION BEING USED
"""
import os
from app.core.config import settings

def check_actual_config():
    """Check what configuration is actually loaded"""
    
    print("🔧 ACTUAL CONFIGURATION IN USE")
    print("=" * 50)
    
    # Check .env file
    print("📁 .ENV FILE CONTENT:")
    try:
        with open(".env", "r") as f:
            env_content = f.read()
            # Mask passwords
            for line in env_content.split('\n'):
                if 'PASSWORD' in line and '=' in line:
                    key, value = line.split('=', 1)
                    print(f"  {key}=***")
                else:
                    print(f"  {line}")
    except Exception as e:
        print(f"  Error reading .env: {e}")
    
    print("\n📋 SETTINGS ATTRIBUTES:")
    try:
        # Get all settings attributes
        attrs = [attr for attr in dir(settings) if not attr.startswith('_')]
        for attr in attrs:
            try:
                value = getattr(settings, attr)
                if value and 'PASSWORD' in attr:
                    print(f"  {attr}: ***")
                elif value:
                    print(f"  {attr}: {value}")
            except:
                print(f"  {attr}: <cannot access>")
    except Exception as e:
        print(f"Error reading settings: {e}")
    
    print("\n🔗 DATABASE URL CONSTRUCTION:")
    try:
        # Try to construct database URL from settings
        db_url = getattr(settings, 'DATABASE_URL', None)
        if db_url:
            print(f"  DATABASE_URL: {db_url.split('@')[0]}***")
        else:
            print("  DATABASE_URL: Not set directly")
            
        # Check if we can construct it from parts
        db_host = getattr(settings, 'database_host', None)
        db_port = getattr(settings, 'database_port', None) 
        db_name = getattr(settings, 'database_name', None)
        db_user = getattr(settings, 'database_user', None)
        
        if all([db_host, db_port, db_name, db_user]):
            print(f"  Constructed from parts: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        else:
            print("  Cannot construct from parts - missing components")
            
    except Exception as e:
        print(f"Error with database URL: {e}")

if __name__ == "__main__":
    check_actual_config()
