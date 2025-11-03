#!/usr/bin/env python3
"""
Check messaging table schema and data
"""
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def check_messaging_schema():
    print("🔍 CHECKING MESSAGING SCHEMA AND DATA")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check messages table schema
        print("\n1. Messages Table Schema:")
        messages_schema = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'messages' 
            ORDER BY ordinal_position;
        """)
        
        for col in messages_schema:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check conversations table schema  
        print("\n2. Conversations Table Schema:")
        conv_schema = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' 
            ORDER BY ordinal_position;
        """)
        
        for col in conv_schema:
            print(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check RLS policies
        print("\n3. RLS Policies:")
        rls_policies = await conn.fetch("""
            SELECT tablename, policyname, permissive, roles, cmd, qual 
            FROM pg_policies 
            WHERE tablename IN ('messages', 'conversations');
        """)
        
        if rls_policies:
            for policy in rls_policies:
                print(f"   {policy['tablename']}.{policy['policyname']}: {policy['cmd']} for {policy['roles']}")
        else:
            print("   No RLS policies found for messaging tables")
        
        # Check recent data
        print("\n4. Recent Conversations:")
        recent_convos = await conn.fetch("""
            SELECT id, title, created_by, created_at 
            FROM conversations 
            ORDER BY created_at DESC 
            LIMIT 3;
        """)
        
        for convo in recent_convos:
            print(f"   - {convo['title']} (ID: {convo['id']}) by {convo['created_by']}")
        
        # Check if we can insert a test message
        if recent_convos:
            test_convo = recent_convos[0]
            print(f"\n5. Testing message insert in conversation: {test_convo['id']}")
            
            try:
                # Try to insert a message
                message_id = await conn.fetchval("""
                    INSERT INTO messages (conversation_id, sender_id, content, content_type)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id;
                """, test_convo['id'], test_convo['created_by'], "Schema test message", "text")
                
                print(f"   ✅ Message inserted successfully! ID: {message_id}")
                
                # Clean up
                await conn.execute("DELETE FROM messages WHERE id = $1", message_id)
                print("   ✅ Test message cleaned up")
                
            except Exception as e:
                print(f"   ❌ Failed to insert message: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_messaging_schema())
