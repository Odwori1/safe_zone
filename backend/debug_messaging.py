#!/usr/bin/env python3
"""
Debug script for messaging system issues
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.crud.messages import create_message, get_conversation_by_id
from app.schemas.messages import MessageCreate

async def debug_messaging():
    print("🔧 DEBUGGING MESSAGING SYSTEM")
    
    # Test database connection
    async for db in get_db():
        try:
            print("1. Testing database connection...")
            
            # Check if conversations table exists
            result = await db.fetchval("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conversations')")
            print(f"   Conversations table exists: {result}")
            
            result = await db.fetchval("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'messages')")
            print(f"   Messages table exists: {result}")
            
            # Check recent conversations
            conversations = await db.fetch("SELECT id, title, created_by FROM conversations ORDER BY created_at DESC LIMIT 5")
            print(f"   Recent conversations: {len(conversations)}")
            for conv in conversations:
                print(f"     - {conv['title']} (ID: {conv['id']})")
                
            # Check if we can insert a test message
            if conversations:
                test_conv = conversations[0]
                print(f"2. Testing message creation in conversation: {test_conv['id']}")
                
                try:
                    message_data = MessageCreate(
                        content="Debug test message",
                        content_type="text"
                    )
                    
                    # Try direct database insert first
                    insert_query = """
                    INSERT INTO messages (conversation_id, sender_id, content, content_type)
                    VALUES ($1, $2, $3, $4) RETURNING id
                    """
                    message_id = await db.fetchval(
                        insert_query,
                        test_conv['id'],
                        test_conv['created_by'],
                        "Direct DB test message",
                        "text"
                    )
                    print(f"   ✅ Direct DB insert successful: Message ID {message_id}")
                    
                except Exception as e:
                    print(f"   ❌ Direct DB insert failed: {e}")
                    
        except Exception as e:
            print(f"   ❌ Database check failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_messaging())
