import asyncio
import httpx
import time

async def test_rate_limiting():
    """Test rate limiting with proper endpoint"""
    print("🚦 Testing Rate Limiting on Protected Endpoint...")
    
    base_url = "http://localhost:8001"
    
    # Test on root endpoint (which should have rate limiting)
    async with httpx.AsyncClient() as client:
        print("Making 15 rapid requests to / endpoint...")
        
        requests = []
        start_time = time.time()
        
        for i in range(15):
            requests.append(client.get(f"{base_url}/"))
        
        responses = await asyncio.gather(*requests, return_exceptions=True)
        end_time = time.time()
        
        success_count = 0
        rate_limited_count = 0
        other_errors = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, httpx.Response):
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    print(f"  Request {i+1}: ✅ Rate Limited (429)")
                else:
                    other_errors += 1
                    print(f"  Request {i+1}: ❌ Unexpected status {response.status_code}")
            else:
                other_errors += 1
                print(f"  Request {i+1}: ❌ Error {response}")
        
        print(f"\n📊 Results:")
        print(f"   Time window: {end_time - start_time:.2f} seconds")
        print(f"   Successful: {success_count}")
        print(f"   Rate Limited: {rate_limited_count}")
        print(f"   Other Errors: {other_errors}")
        
        if rate_limited_count > 0:
            print("✅ Rate limiting is WORKING!")
            return True
        else:
            print("❌ Rate limiting may not be active")
            return False

async def main():
    print("🎯 Rate Limiting Validation")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    await asyncio.sleep(1)
    
    success = await test_rate_limiting()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 RATE LIMITING VALIDATION PASSED!")
    else:
        print("⚠️  Rate limiting needs attention")

if __name__ == "__main__":
    asyncio.run(main())
