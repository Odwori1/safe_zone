#!/usr/bin/env python3
"""
Final fix for messaging system - ensure conversation participants
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_messaging_final():
    print("🔧 FINAL MESSAGING SYSTEM FIX")
    print("=" * 35)
    
    db_config = {
        'host': '127.0.0.1',
        'port': 5433,
        'database': 'safe_zone',
        'user': 'safe_zone_app_user',
        'password': 'secure_app_password_2024'
    }
    
    try:
        conn = await asyncpg.connect(**db_config)
        print("✅ Connected to database")
        
        # Step 1: Check conversation participants
        print("\n1. Checking conversation participants...")
        conversations = await conn.fetch("""
            SELECT id, title, created_by FROM conversations 
            ORDER BY created_at DESC LIMIT 5;
        """)
        
        for conv in conversations:
            participants = await conn.fetch("""
                SELECT user_id FROM conversation_participants 
                WHERE conversation_id = $1;
            """, conv['id'])
            
            print(f"   Conversation: {conv['title']} (ID: {conv['id']})")
            print(f"   Participants: {len(participants)}")
            
            # Add creator as participant if missing
            if len(participants) == 0:
                await conn.execute("""
                    INSERT INTO conversation_participants (conversation_id, user_id, joined_at)
                    VALUES ($1, $2, NOW());
                """, conv['id'], conv['created_by'])
                print(f"   ✅ Added creator as participant")
        
        # Step 2: Test message creation
        print("\n2. Testing message creation...")
        if conversations:
            test_conv = conversations[0]
            user_id = test_conv['created_by']
            
            # Set current user for RLS
            await conn.execute(f"SET app.current_user_id = '{user_id}'")
            
            # Test message creation
            try:
                msg_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, sender_id, content, content_type)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id;
                """, test_conv['id'], user_id, "Final fix test message", "text")
                
                print(f"   ✅ MESSAGE CREATION SUCCESSFUL! ID: {msg_id}")
                
                # Clean up
                await conn.execute("DELETE FROM messages WHERE id = $1", msg_id)
                print("   🧹 Test message cleaned up")
                
            except Exception as e:
                print(f"   ❌ Message creation failed: {e}")
        
        await conn.close()
        print("\n🎉 MESSAGING SYSTEM FIXED!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_messaging_final())
