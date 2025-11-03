#!/usr/bin/env python3
"""
Immediate fix for messaging system issues
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_messaging_issues():
    print("🔧 FIXING MESSAGING SYSTEM ISSUES")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check current conversations
        print("\n1. Checking existing conversations...")
        conversations = await conn.fetch("""
            SELECT id, title, created_by, created_at 
            FROM conversations 
            ORDER BY created_at DESC 
            LIMIT 5;
        """)
        
        print(f"Found {len(conversations)} conversations:")
        for conv in conversations:
            print(f"   - {conv['title']} (ID: {conv['id']}) by {conv['created_by']}")
        
        # Check messages in those conversations
        print("\n2. Checking messages in conversations...")
        for conv in conversations:
            messages = await conn.fetch("""
                SELECT id, content, sender_id, created_at 
                FROM messages 
                WHERE conversation_id = $1 
                ORDER BY created_at DESC 
                LIMIT 3;
            """, conv['id'])
            
            print(f"   Conversation '{conv['title']}': {len(messages)} messages")
            for msg in messages:
                print(f"     - {msg['content'][:50]}... (by {msg['sender_id']})")
        
        # Test creating a message directly in database
        if conversations:
            test_conv = conversations[0]
            print(f"\n3. Testing direct message creation in '{test_conv['title']}'...")
            
            try:
                # Insert message directly
                message_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, sender_id, content, content_type)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id;
                """, test_conv['id'], test_conv['created_by'], "Direct DB test message", "text")
                
                print(f"   ✅ Direct DB insert SUCCESSFUL! Message ID: {message_id}")
                
                # Verify it was inserted
                new_msg = await conn.fetchrow("SELECT * FROM messages WHERE id = $1", message_id)
                print(f"   ✅ Message verified: {new_msg['content']}")
                
                # Clean up
                await conn.execute("DELETE FROM messages WHERE id = $1", message_id)
                print("   ✅ Test message cleaned up")
                
            except Exception as e:
                print(f"   ❌ Direct DB insert FAILED: {e}")
                print(f"   Error details: {str(e)}")
        
        # Check RLS policies
        print("\n4. Checking RLS policies...")
        rls_status = await conn.fetchval("""
            SELECT relrowsecurity FROM pg_class WHERE relname = 'messages';
        """)
        print(f"   Messages table RLS enabled: {rls_status}")
        
        rls_status = await conn.fetchval("""
            SELECT relrowsecurity FROM pg_class WHERE relname = 'conversations';
        """)
        print(f"   Conversations table RLS enabled: {rls_status}")
        
        # Check policies
        policies = await conn.fetch("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
            FROM pg_policies 
            WHERE tablename IN ('messages', 'conversations');
        """)
        
        if policies:
            print("   Existing RLS policies:")
            for policy in policies:
                print(f"     - {policy['tablename']}.{policy['policyname']}: {policy['cmd']}")
        else:
            print("   ❌ No RLS policies found!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(fix_messaging_issues())
