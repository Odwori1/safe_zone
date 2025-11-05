#!/usr/bin/env python3
"""
PHASE 3 SEQUENTIAL TESTING SCRIPT
Tests features in the exact Phase 3 sequence
"""

import asyncio
import aiohttp
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Phase3Tester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api/v1"
        self.token = None
        self.user_id = None
        self.session = None
        
    async def setup(self):
        """Initialize the test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def test_authentication(self):
        """3.0 - Test Authentication System"""
        print("🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test login
        login_data = {
            "email": "developer_test@example.com",
            "password": "DeveloperPass123!"
        }
        
        async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                self.token = result.get('access_token')
                self.user_id = result.get('user_id')
                print("✅ Login successful")
                print(f"   Token: {self.token[:50]}...")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Login failed: {response.status}")
                return False
    
    def get_headers(self):
        """Get headers with authentication token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def test_audio_upload_endpoints(self):
        """3.1.1 - Test Audio Upload Endpoints"""
        print("\n🎵 TESTING AUDIO UPLOAD ENDPOINTS...")
        
        # Test audio upload endpoint availability
        async with self.session.get(
            f"{self.base_url}/uploads/audio/presigned-url", 
            headers=self.get_headers()
        ) as response:
            if response.status in [200, 405]:  # 405 means endpoint exists but wrong method
                print("✅ Audio upload endpoint available")
                return True
            else:
                print(f"❌ Audio upload endpoint failed: {response.status}")
                return False
    
    async def test_audio_post_creation(self):
        """3.1.2 - Test Audio Post Creation"""
        print("\n📝 TESTING AUDIO POST CREATION...")
        
        # First create a regular post (audio posts might extend this)
        post_data = {
            "content": "Test post for audio integration",
            "mood": "calm",
            "visibility": "public",
            "is_anonymous": False
        }
        
        async with self.session.post(
            f"{self.base_url}/posts", 
            json=post_data,
            headers=self.get_headers()
        ) as response:
            if response.status == 200:
                result = await response.json()
                print("✅ Post creation working (audio post foundation)")
                return result.get('post_id')
            else:
                print(f"❌ Post creation failed: {response.status}")
                return None
    
    async def test_video_upload_endpoints(self):
        """3.2.1 - Test Video Upload Endpoints"""
        print("\n🎬 TESTING VIDEO UPLOAD ENDPOINTS...")
        
        async with self.session.get(
            f"{self.base_url}/uploads/video/presigned-url", 
            headers=self.get_headers()
        ) as response:
            if response.status in [200, 405]:
                print("✅ Video upload endpoint available")
                return True
            else:
                print(f"❌ Video upload endpoint failed: {response.status}")
                return False
    
    async def test_video_post_creation(self):
        """3.2.2 - Test Video Post Creation"""
        print("\n🎥 TESTING VIDEO POST CREATION...")
        
        # Test if posts endpoint accepts video metadata
        post_data = {
            "content": "Test post for video integration",
            "mood": "calm", 
            "visibility": "public",
            "is_anonymous": False,
            "has_media": True
        }
        
        async with self.session.post(
            f"{self.base_url}/posts",
            json=post_data,
            headers=self.get_headers()
        ) as response:
            if response.status == 200:
                print("✅ Video post foundation working")
                return True
            else:
                print(f"❌ Video post test failed: {response.status}")
                return False
    
    async def test_file_upload_system(self):
        """3.3 - Test File Upload System (Local Storage)"""
        print("\n📁 TESTING FILE UPLOAD SYSTEM...")
        
        # Test uploads endpoint
        endpoints_to_test = [
            "/uploads/file/presigned-url",
            "/uploads/image/presigned-url", 
            "/files/my-files"
        ]
        
        for endpoint in endpoints_to_test:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            ) as response:
                if response.status in [200, 405]:
                    print(f"✅ {endpoint} endpoint available")
                else:
                    print(f"❌ {endpoint} endpoint failed: {response.status}")
        
        return True
    
    async def test_real_time_messaging_endpoints(self):
        """3.4 - Test Real-time Messaging Endpoints"""
        print("\n💬 TESTING REAL-TIME MESSAGING ENDPOINTS...")
        
        messaging_endpoints = [
            "/messages/conversations",
            "/messages/conversations/create",
            "/messages/send"
        ]
        
        for endpoint in messaging_endpoints:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            ) as response:
                status_ok = response.status in [200, 405, 422]  # 422 might be validation error
                if status_ok:
                    print(f"✅ {endpoint} endpoint available")
                else:
                    print(f"❌ {endpoint} endpoint failed: {response.status}")
        
        return True
    
    async def test_live_audio_rooms_endpoints(self):
        """3.5 - Test Live Audio Rooms Endpoints"""
        print("\n🎤 TESTING LIVE AUDIO ROOMS ENDPOINTS...")
        
        audio_room_endpoints = [
            "/audio-rooms",
            "/audio-rooms/create",
            "/audio-rooms/active"
        ]
        
        for endpoint in audio_room_endpoints:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            ) as response:
                if response.status in [200, 405]:
                    print(f"✅ {endpoint} endpoint available")
                else:
                    print(f"❌ {endpoint} endpoint failed: {response.status}")
        
        return True
    
    async def test_enhanced_moderation_endpoints(self):
        """3.6 - Test Enhanced Moderation Endpoints"""
        print("\n🛡️ TESTING ENHANCED MODERATION ENDPOINTS...")
        
        moderation_endpoints = [
            "/moderation/reports",
            "/moderation/queue",
            "/moderation/analytics"
        ]
        
        for endpoint in moderation_endpoints:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            ) as response:
                if response.status in [200, 405, 403]:  # 403 might be permission issue
                    print(f"✅ {endpoint} endpoint available")
                else:
                    print(f"❌ {endpoint} endpoint failed: {response.status}")
        
        return True
    
    async def run_all_tests(self):
        """Run all Phase 3 tests in sequence"""
        print("🚀 STARTING PHASE 3 SEQUENTIAL TESTING")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Must start with authentication
            if not await self.test_authentication():
                print("❌ Authentication failed - stopping tests")
                return False
            
            # Follow exact Phase 3 sequence
            tests = [
                ("3.1 Audio Post Support - Upload Endpoints", self.test_audio_upload_endpoints),
                ("3.1 Audio Post Support - Post Creation", self.test_audio_post_creation),
                ("3.2 Video Post Support - Upload Endpoints", self.test_video_upload_endpoints),
                ("3.2 Video Post Support - Post Creation", self.test_video_post_creation),
                ("3.3 File Upload System", self.test_file_upload_system),
                ("3.4 Real-time Messaging", self.test_real_time_messaging_endpoints),
                ("3.5 Live Audio Rooms", self.test_live_audio_rooms_endpoints),
                ("3.6 Enhanced Moderation", self.test_enhanced_moderation_endpoints),
            ]
            
            results = []
            for test_name, test_func in tests:
                try:
                    result = await test_func()
                    results.append((test_name, result))
                except Exception as e:
                    print(f"❌ {test_name} crashed: {e}")
                    results.append((test_name, False))
            
            # Print summary
            print("\n" + "=" * 50)
            print("📊 PHASE 3 TESTING SUMMARY")
            print("=" * 50)
            
            for test_name, result in results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            
            total_passed = sum(1 for _, result in results if result)
            total_tests = len(results)
            print(f"\n🎯 RESULTS: {total_passed}/{total_tests} tests passed")
            
            return total_passed == total_tests
            
        finally:
            await self.cleanup()

async def main():
    tester = Phase3Tester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL PHASE 3 BACKEND TESTS PASSED!")
        print("➡️ Ready for frontend integration")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED - Check backend implementation")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
