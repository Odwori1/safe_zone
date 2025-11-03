#!/usr/bin/env python3
"""
Check database status and basic connectivity
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_database():
    print("🔍 CHECKING DATABASE STATUS")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        return
    
    print(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unable to parse'}")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection SUCCESSFUL")
        
        # Check if messaging tables exist
        tables = ['conversations', 'messages', 'conversation_participants']
        
        for table in tables:
            exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}' exists: {exists}")
        
        # Check message creation directly
        print("\n🔧 Testing message creation directly...")
        
        # Get a user and conversation to test with
        users = await conn.fetch("SELECT id FROM users LIMIT 1")
        if users:
            user_id = users[0]['id']
            print(f"Found user: {user_id}")
            
            # Create a test conversation
            conv_id = await conn.fetchval("""
                INSERT INTO conversations (title, created_by, is_group)
                VALUES ($1, $2, $3)
                RETURNING id
            """, "Test Conversation", user_id, False)
            
            print(f"Created test conversation: {conv_id}")
            
            # Try to create a message
            try:
                msg_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, sender_id, content, content_type)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, conv_id, user_id, "Test message", "text")
                
                print(f"✅ Message creation SUCCESSFUL! Message ID: {msg_id}")
                
                # Clean up
                await conn.execute("DELETE FROM messages WHERE id = $1", msg_id)
                await conn.execute("DELETE FROM conversations WHERE id = $1", conv_id)
                print("✅ Test data cleaned up")
                
            except Exception as e:
                print(f"❌ Message creation FAILED: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection FAILED: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("1. Is PostgreSQL running? Try: sudo service postgresql start")
        print("2. Check DATABASE_URL in .env file")
        print("3. Verify PostgreSQL is listening on port 5432")

if __name__ == "__main__":
    asyncio.run(check_database())
