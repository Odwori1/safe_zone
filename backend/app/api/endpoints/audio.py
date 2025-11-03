from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.core.security import get_current_user
from app.schemas.user import User
from app.database.database import database
import json

router = APIRouter()

@router.get("/rooms")
async def get_audio_rooms(
    current_user: User = Depends(get_current_user)
):
    """Get list of audio rooms - WORKING VERSION"""
    try:
        print(f"🔊 AUDIO ENDPOINT: Fetching audio rooms for user {current_user.id}")
        
        async with database.pool.acquire() as conn:
            print("✅ Database connection acquired")
            
            # First, check if we have any rooms
            room_count = await conn.fetchval("SELECT COUNT(*) FROM audio_rooms WHERE is_active = true")
            print(f"📊 Total active rooms: {room_count}")
            
            # If no rooms, return empty array immediately
            if room_count == 0:
                print("ℹ️ No rooms found, returning empty array")
                return []
            
            # Get rooms with all fields
            rooms = await conn.fetch("""
                SELECT 
                    id,
                    title,
                    description,
                    created_by,
                    visibility,
                    max_participants,
                    room_type,
                    is_active,
                    is_locked,
                    locked_by,
                    lock_reason,
                    locked_at,
                    current_participants,
                    host_username,
                    created_at,
                    updated_at
                FROM audio_rooms 
                WHERE is_active = true 
                ORDER BY created_at DESC 
                LIMIT 50
            """)
            
            print(f"📊 Found {len(rooms)} rooms to process")
            
            # Convert to dictionaries with proper null handling
            room_list = []
            for room in rooms:
                room_dict = dict(room)
                
                # Ensure all fields have proper values
                processed_room = {
                    "id": str(room_dict["id"]),
                    "title": room_dict["title"] or "Untitled Room",
                    "description": room_dict["description"] or "",
                    "created_by": str(room_dict["created_by"]),
                    "visibility": room_dict["visibility"] or "public",
                    "max_participants": room_dict["max_participants"] or 10,
                    "room_type": room_dict["room_type"] or "support",
                    "is_active": bool(room_dict["is_active"]),
                    "is_locked": bool(room_dict["is_locked"]),
                    "locked_by": str(room_dict["locked_by"]) if room_dict["locked_by"] else None,
                    "lock_reason": room_dict["lock_reason"] or None,
                    "locked_at": room_dict["locked_at"].isoformat() if room_dict["locked_at"] else None,
                    "current_participants": room_dict["current_participants"] or 0,
                    "host_username": room_dict["host_username"] or "",
                    "created_at": room_dict["created_at"].isoformat(),
                    "updated_at": room_dict["updated_at"].isoformat()
                }
                room_list.append(processed_room)
            
            print(f"✅ Successfully returning {len(room_list)} rooms")
            return room_list
            
    except Exception as e:
        print(f"❌ AUDIO ENDPOINT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty array on error
        return []

@router.post("/rooms")
async def create_audio_room(
    current_user: User = Depends(get_current_user)
):
    """Create a new audio room - WORKING VERSION"""
    try:
        print(f"🔊 CREATE AUDIO ROOM: Starting for user {current_user.id}")
        
        async with database.pool.acquire() as conn:
            # Get username for host_username
            username = await conn.fetchval(
                "SELECT username FROM users WHERE id = $1", 
                current_user.id
            )
            
            # Create a test room
            result = await conn.fetchrow("""
                INSERT INTO audio_rooms (
                    title, description, created_by, 
                    visibility, max_participants, room_type,
                    host_username, current_participants
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """, 
            "Test Support Room", 
            "A test audio room for mental health discussions",
            current_user.id,
            "public",
            10,
            "support",
            username or "user",
            0
            )
            
            room_dict = dict(result)
            
            # Format the response properly
            formatted_room = {
                "id": str(room_dict["id"]),
                "title": room_dict["title"],
                "description": room_dict["description"],
                "created_by": str(room_dict["created_by"]),
                "visibility": room_dict["visibility"],
                "max_participants": room_dict["max_participants"],
                "room_type": room_dict["room_type"],
                "is_active": room_dict["is_active"],
                "is_locked": room_dict["is_locked"],
                "locked_by": str(room_dict["locked_by"]) if room_dict["locked_by"] else None,
                "lock_reason": room_dict["lock_reason"],
                "locked_at": room_dict["locked_at"].isoformat() if room_dict["locked_at"] else None,
                "current_participants": room_dict["current_participants"],
                "host_username": room_dict["host_username"],
                "created_at": room_dict["created_at"].isoformat(),
                "updated_at": room_dict["updated_at"].isoformat()
            }
            
            print(f"✅ Room created successfully: {formatted_room['id']}")
            return formatted_room
            
    except Exception as e:
        print(f"❌ CREATE AUDIO ROOM ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.get("/test")
async def test_audio_endpoint():
    """Test endpoint without authentication"""
    return {
        "message": "Audio endpoint is working!",
        "status": "success"
    }

@router.get("/debug")
async def debug_audio_tables(current_user: User = Depends(get_current_user)):
    """Debug endpoint to check table structure"""
    try:
        async with database.pool.acquire() as conn:
            # Check table structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'audio_rooms'
                ORDER BY ordinal_position
            """)
            
            column_info = [dict(col) for col in columns]
            
            # Check sample data
            sample_data = await conn.fetch("SELECT * FROM audio_rooms LIMIT 1")
            sample_dict = dict(sample_data[0]) if sample_data else {}
            
            return {
                "table_columns": column_info,
                "sample_data": sample_dict,
                "total_rooms": await conn.fetchval("SELECT COUNT(*) FROM audio_rooms")
            }
            
    except Exception as e:
        return {"error": str(e)}
