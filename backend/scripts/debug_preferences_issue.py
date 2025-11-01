#!/usr/bin/env python3
"""
Debug the preferences schema issue in detail
"""

import asyncio
import aiohttp
import os

async def debug_preferences():
    token = os.getenv('TEST_TOKEN')
    if not token:
        print("❌ No TEST_TOKEN")
        return
    
    base_url = "http://localhost:8001/api/v1/crisis-support"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Debugging preferences endpoint...")
        
        # Test the preferences endpoint and get the full error
        async with session.get(f"{base_url}/preferences", headers=headers) as resp:
            error_text = await resp.text()
            print(f"Status: {resp.status}")
            print(f"Full error response:\n{error_text}")
            
            # If it's a 500 error, let's check what the actual data looks like
            if resp.status == 500:
                print("\n🧪 Let's check what data the CRUD returns...")
                import asyncpg
                from app.database.database import database
                
                test_user_id = "8808956b-11fb-4253-91ef-98b9902ffbc8"
                
                try:
                    await database.connect()
                    from app.crud.crisis import crisis_crud
                    
                    # Get the raw data from CRUD
                    raw_data = await crisis_crud.get_user_crisis_preferences(test_user_id)
                    print(f"Raw CRUD data type: {type(raw_data)}")
                    if raw_data:
                        print(f"Raw CRUD data: {dict(raw_data)}")
                        
                        # Try to create the response manually to see where it fails
                        from app.schemas.crisis import UserCrisisPreferencesResponse
                        try:
                            response_obj = UserCrisisPreferencesResponse(**dict(raw_data))
                            print("✅ Manual schema creation SUCCESS!")
                            print(f"Response object: {response_obj}")
                        except Exception as e:
                            print(f"❌ Manual schema creation FAILED: {e}")
                            
                except Exception as e:
                    print(f"❌ CRUD test failed: {e}")
                finally:
                    await database.close()

if __name__ == "__main__":
    asyncio.run(debug_preferences())
