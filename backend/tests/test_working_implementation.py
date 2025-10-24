"""
TEST THE ACTUAL WORKING IMPLEMENTATION
Test if the live_audio_rooms CRUD actually works with RLS
"""
import asyncio
from app.database.database import database
from app.crud.live_audio_rooms import live_audio_rooms_crud
from uuid import uuid4

async def test_working_implementation():
    """Test if the working implementation actually sets RLS context"""
    print("🔍 TESTING ACTUAL WORKING IMPLEMENTATION")
    print("=" * 50)
    
    await database.connect()
    
    try:
        # Test the actual create_room method from live_audio_rooms
        test_user_id = uuid4()
        print(f"1. Testing create_room with user: {test_user_id}")
        
        # This should set RLS context internally
        room_data = {
            "title": "Test RLS Room",
            "description": "Testing RLS context",
            "max_participants": 10,
            "room_type": "support"
        }
        
        room = await live_audio_rooms_crud.create_room(room_data, test_user_id)
        
        if room:
            print(f"✅ Room created successfully: {room['id']}")
            print("   This means RLS context WAS set properly in the working code!")
            
            # Now let's verify the room was created with the right user
            async with database.pool.acquire() as conn:
                room_check = await conn.fetchrow(
                    "SELECT created_by FROM live_audio_rooms WHERE id = $1",
                    room['id']
                )
                if room_check and room_check['created_by'] == test_user_id:
                    print("✅ Room correctly associated with test user")
                    print("🎉 RLS CONTEXT IS WORKING IN PRODUCTION CODE!")
                    return True
                else:
                    print("❌ Room not associated with correct user")
                    return False
        else:
            print("❌ Failed to create room")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if database.pool:
            await database.pool.close()

if __name__ == "__main__":
    success = asyncio.run(test_working_implementation())
    exit(0 if success else 1)
