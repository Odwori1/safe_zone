import asyncio
import aiohttp
import json

async def check_coverage():
    BASE_URL = "http://localhost:8001/api/v1"
    
    # Get token first
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {
            "email": "developer_test@example.com",
            "password": "DeveloperPass123!"
        }
        
        print("🔐 Logging in...")
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result['access_token']
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status}")
                return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("\n📋 PHASE 2.7 FEED SYSTEM COVERAGE CHECK")
        print("=" * 60)
        
        # Check each requirement
        requirements = {
            "Personalized feed algorithms": ["/posts/feed/personal"],
            "Content filtering by mood/type": [
                "/posts/feed/personal?mood=happy",
                "/posts/feed/personal?visibility=public"
            ],
            "Feed customization": ["/posts/feed/personal?limit=5&skip=0"],
            "Content discovery": ["/posts/feed/discover"],
            "Saved posts/collections": ["/posts/saved", "/collections"],
            "Feed export options": ["/posts/export", "/feed/export"]
        }
        
        coverage_status = {}
        
        for requirement, endpoints in requirements.items():
            print(f"\n🔍 Checking: {requirement}")
            requirement_covered = False
            
            for endpoint in endpoints:
                try:
                    # For GET endpoints
                    if endpoint.startswith("/posts/feed/personal?"):
                        # Test with parameters
                        async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                            if response.status == 200:
                                print(f"   ✅ {endpoint} - WORKING")
                                requirement_covered = True
                            else:
                                print(f"   ❌ {endpoint} - Failed (Status: {response.status})")
                    elif endpoint in ["/posts/saved", "/collections", "/posts/export", "/feed/export"]:
                        # These likely don't exist yet
                        async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                            if response.status == 200:
                                print(f"   ✅ {endpoint} - WORKING")
                                requirement_covered = True
                            elif response.status == 404:
                                print(f"   ⏳ {endpoint} - NOT IMPLEMENTED")
                            else:
                                print(f"   ❌ {endpoint} - Failed (Status: {response.status})")
                    else:
                        # Regular endpoints
                        async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                            if response.status == 200:
                                print(f"   ✅ {endpoint} - WORKING")
                                requirement_covered = True
                            else:
                                print(f"   ❌ {endpoint} - Failed (Status: {response.status})")
                except Exception as e:
                    print(f"   ❌ {endpoint} - Error: {e}")
            
            coverage_status[requirement] = requirement_covered
        
        print("\n" + "=" * 60)
        print("🎯 PHASE 2.7 COMPLETION SUMMARY")
        print("=" * 60)
        
        implemented = []
        not_implemented = []
        
        for requirement, covered in coverage_status.items():
            if covered:
                implemented.append(requirement)
            else:
                not_implemented.append(requirement)
        
        print("\n✅ IMPLEMENTED:")
        for item in implemented:
            print(f"   ✓ {item}")
        
        print("\n⏳ STILL NEEDS IMPLEMENTATION:")
        for item in not_implemented:
            print(f"   □ {item}")
        
        completion_percentage = (len(implemented) / len(coverage_status)) * 100
        print(f"\n📊 COMPLETION: {completion_percentage:.1f}%")
        
        if not_implemented:
            print(f"\n🔧 NEXT STEPS: Need to implement:")
            for item in not_implemented:
                print(f"   - {item}")

if __name__ == "__main__":
    asyncio.run(check_coverage())
