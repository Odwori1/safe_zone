#!/usr/bin/env python3
"""
System Health Check - Quick verification of all critical components
"""
import sys

def health_check():
    print("🏥 SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    # Test imports for all critical components
    components = [
        ("Authentication", "app.core.security"),
        ("Database", "app.database.database"),
        ("Posts Schemas", "app.schemas.post"),
        ("Posts CRUD", "app.crud.post_audio"),
        ("Posts Endpoints", "app.api.endpoints.posts"),
        ("Uploads Endpoints", "app.api.endpoints.uploads"),
        ("Audio Support", "app.schemas.post.PostContentType.AUDIO"),
        ("Video Support", "app.schemas.post.PostContentType.VIDEO"),
        ("File Upload Handler", "app.utils.file_upload.file_upload_handler"),
    ]
    
    healthy = True
    for component_name, import_path in components:
        try:
            if "." in import_path:
                # Handle class attributes
                if "PostContentType" in import_path:
                    from app.schemas.post import PostContentType
                    if "AUDIO" in import_path:
                        _ = PostContentType.AUDIO
                    elif "VIDEO" in import_path:
                        _ = PostContentType.VIDEO
                else:
                    # Regular module import
                    exec(f"import {import_path}")
            else:
                __import__(import_path)
            print(f"✅ {component_name}")
        except Exception as e:
            print(f"❌ {component_name}: {e}")
            healthy = False
    
    # Test server startup
    try:
        from app.main import app
        print("✅ Server Application")
    except Exception as e:
        print(f"❌ Server Application: {e}")
        healthy = False
    
    print("\n" + "=" * 50)
    if healthy:
        print("🎉 SYSTEM HEALTH: EXCELLENT")
        print("   All components are properly configured")
    else:
        print("⚠️  SYSTEM HEALTH: ISSUES DETECTED")
        print("   Some components need attention")
    
    return healthy

if __name__ == "__main__":
    healthy = health_check()
    sys.exit(0 if healthy else 1)
