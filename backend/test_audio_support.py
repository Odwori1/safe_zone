#!/usr/bin/env python3
"""
Test script for Audio Post Support
Phase 3, Item 1: Audio Post Support
"""

import asyncio
import asyncpg
import sys
import os
from uuid import UUID

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings
from app.database.database import database

async def test_audio_schema():
    """Test that posts table has audio support columns"""
    print("🧪 Testing Audio Support Schema...")
    
    conn = None
    try:
        conn = await asyncpg.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name
        )
        
        # Check if audio columns exist in posts table
        print("📊 Checking posts table audio columns...")
        audio_columns = ['audio_url', 'audio_duration', 'file_size', 'mime_type']
        
        for column in audio_columns:
            column_exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'posts' AND column_name = '{column}'
                );
            """)
            
            if column_exists:
                print(f"   ✅ {column} column exists")
            else:
                print(f"   ❌ {column} column missing")
                return False
        
        # Check if file_uploads table exists
        print("\n🗂️ Checking file_uploads table...")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'file_uploads'
            );
        """)
        
        if table_exists:
            print("   ✅ file_uploads table exists")
            
            # Check RLS is enabled
            rls_enabled = await conn.fetchval("""
                SELECT relrowsecurity FROM pg_class WHERE relname = 'file_uploads';
            """)
            
            if rls_enabled:
                print("   ✅ RLS enabled on file_uploads")
            else:
                print("   ❌ RLS not enabled on file_uploads")
                return False
        else:
            print("   ❌ file_uploads table missing")
            return False
        
        print("🎉 Audio schema test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio schema test failed: {e}")
        return False
    finally:
        if conn:
            await conn.close()

async def test_audio_crud():
    """Test CRUD operations for audio posts"""
    print("\n🧪 Testing Audio Posts CRUD Operations...")
    
    try:
        # Initialize database connection
        await database.connect()
        
        # Use an existing test user
        from app.crud.user import user_crud
        test_user = await user_crud.get_by_email("api_test@example.com")
        if not test_user:
            print("❌ Test user not found")
            return False
        
        user_id = test_user['id']
        print(f"✅ Using test user: {test_user.get('email', 'Unknown')}")
        
        # Test creating audio post
        from app.crud.post_audio import post_crud
        from app.schemas.post import PostCreate, PostContentType
        
        audio_post_data = PostCreate(
            content="This is an audio post with description",
            content_type=PostContentType.AUDIO,
            audio_url="/uploads/test-audio.mp3",
            audio_duration=120,
            file_size=1024000,
            mime_type="audio/mpeg",
            mood="thoughtful",
            visibility="public",
            is_anonymous=False
        )
        
        created_audio_post = await post_crud.create(user_id, audio_post_data)
        if created_audio_post and created_audio_post['content_type'] == 'audio':
            print("✅ Create audio post: PASS")
            audio_post_id = created_audio_post['id']
        else:
            print("❌ Create audio post: FAIL")
            return False
        
        # Test getting audio posts
        audio_posts = await post_crud.get_audio_posts(user_id)
        if audio_posts and len(audio_posts) > 0:
            print("✅ Get audio posts: PASS")
            print(f"   Found {len(audio_posts)} audio posts")
        else:
            print("❌ Get audio posts: FAIL")
            return False
        
        # Test file upload record creation
        from app.schemas.post_audio import FileUploadCreate
        
        file_upload_data = FileUploadCreate(
            filename="test-file.mp3",
            original_filename="original-test.mp3",
            file_url="/uploads/test-file.mp3",
            file_size=1024000,
            mime_type="audio/mpeg",
            duration=180
        )
        
        file_record = await post_crud.create_file_upload_record(user_id, file_upload_data)
        if file_record:
            print("✅ Create file upload record: PASS")
            file_id = file_record['id']
        else:
            print("❌ Create file upload record: FAIL")
            return False
        
        # Test associating file with post
        association_success = await post_crud.update_file_upload_with_post(file_id, audio_post_id)
        if association_success:
            print("✅ Associate file with post: PASS")
        else:
            print("❌ Associate file with post: FAIL")
            return False
        
        # Test getting user file uploads
        user_uploads = await post_crud.get_user_file_uploads(user_id)
        if user_uploads and len(user_uploads) > 0:
            print("✅ Get user file uploads: PASS")
            print(f"   Found {len(user_uploads)} file uploads")
        else:
            print("❌ Get user file uploads: FAIL")
            return False
        
        # Clean up test data
        await post_crud.delete(audio_post_id, user_id)
        print("✅ Test data cleaned up")
        
        print("🎉 Audio CRUD test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await database.close()

async def test_file_upload_utility():
    """Test file upload utility functions"""
    print("\n🧪 Testing File Upload Utilities...")
    
    try:
        from app.utils.file_upload import file_upload_handler
        
        # Test audio type validation
        valid_types = ['audio/mpeg', 'audio/wav', 'audio/ogg']
        invalid_types = ['image/jpeg', 'video/mp4', 'text/plain']
        
        for mime_type in valid_types:
            if file_upload_handler._is_valid_audio_type(mime_type):
                print(f"✅ Valid audio type: {mime_type}")
            else:
                print(f"❌ Should be valid: {mime_type}")
                return False
        
        for mime_type in invalid_types:
            if not file_upload_handler._is_valid_audio_type(mime_type):
                print(f"✅ Invalid type rejected: {mime_type}")
            else:
                print(f"❌ Should be invalid: {mime_type}")
                return False
        
        # Test file extension mapping
        test_cases = [
            ('test.mp3', 'audio/mpeg', '.mp3'),
            ('test', 'audio/wav', '.wav'),
            ('test.unknown', 'audio/ogg', '.ogg')
        ]
        
        for filename, mime_type, expected_ext in test_cases:
            actual_ext = file_upload_handler._get_file_extension(filename, mime_type)
            if actual_ext == expected_ext:
                print(f"✅ File extension mapping: {filename} -> {actual_ext}")
            else:
                print(f"❌ File extension wrong: {filename} -> {actual_ext} (expected {expected_ext})")
                return False
        
        print("🎉 File upload utility test passed!")
        return True
        
    except Exception as e:
        print(f"❌ File upload utility test failed: {e}")
        return False

async def main():
    """Run all audio support tests"""
    print("🚀 Starting Audio Post Support Tests...")
    print("Phase 3, Item 1: Audio Post Support")
    print("=" * 60)
    
    schema_success = await test_audio_schema()
    crud_success = await test_audio_crud()
    utility_success = await test_file_upload_utility()
    
    if schema_success and crud_success and utility_success:
        print("\n" + "=" * 60)
        print("🎉 ALL AUDIO POST SUPPORT TESTS PASSED!")
        print("✅ Schema updates: COMPLETE")
        print("✅ CRUD operations: WORKING")
        print("✅ File upload utilities: WORKING")
        print("✅ Audio post creation: WORKING")
        print("✅ File tracking: WORKING")
        print("\n🚀 Phase 3, Item 1: Audio Post Support - COMPLETE!")
        print("📋 Ready for Phase 3, Item 2: Video Post Support")
        return True
    else:
        print("\n❌ SOME AUDIO SUPPORT TESTS FAILED")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
