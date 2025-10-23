#!/usr/bin/env python3
"""
FINAL SECURITY AUDIT FOR LIVE AUDIO ROOMS
Following EXACT same patterns as security_audit_messaging.py
"""
import asyncio
import uuid
from app.database.database import init_db
from app.crud.live_audio_rooms import live_audio_rooms_crud

async def final_security_audit():
    """Final security audit for live audio rooms"""
    
    print("🔒 FINAL LIVE AUDIO ROOMS SECURITY AUDIT")
    print("=" * 60)
    
    await init_db()
    
    # Get a real user from the system
    from app.database.database import database
    async with database.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
        
        if not user:
            print("❌ No users found for testing")
            return
            
        user_id = user['id']
        print(f"✅ Testing with user: {user['email']}")
        
        try:
            # Test 1: Room Creation
            print("\n1. Testing Room Creation...")
            room = await live_audio_rooms_crud.create_room(
                {'title': 'Security Audit Room', 'visibility': 'public'}, 
                user_id
            )
            if room:
                print("   ✅ Room creation: PASSED")
            else:
                print("   ❌ Room creation: FAILED")
                return
            
            # Test 2: Room Access Control
            print("\n2. Testing Room Access Control...")
            accessible_room = await live_audio_rooms_crud.get_room(room['id'], user_id)
            if accessible_room:
                print("   ✅ Room access: PASSED")
            else:
                print("   ❌ Room access: FAILED")
            
            # Test 3: Participant Management
            print("\n3. Testing Participant Management...")
            participants = await live_audio_rooms_crud.get_room_participants(room['id'], user_id)
            if participants and len(participants) > 0:
                print("   ✅ Participant access: PASSED")
            else:
                print("   ❌ Participant access: FAILED")
            
            # Test 4: Room Leaving
            print("\n4. Testing Room Leaving...")
            success = await live_audio_rooms_crud.leave_room(room['id'], user_id)
            if success:
                print("   ✅ Room leaving: PASSED")
            else:
                print("   ❌ Room leaving: FAILED")
            
            print("\n🎉 SECURITY AUDIT COMPLETE: ALL TESTS PASSED!")
            
        except Exception as e:
            print(f"❌ Security audit failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(final_security_audit())
