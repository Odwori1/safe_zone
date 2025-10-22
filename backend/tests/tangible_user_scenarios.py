#!/usr/bin/env python3
"""
TANGIBLE USER SCENARIOS TEST
Creates real users and tests messaging security in practice
"""
import asyncio
import aiohttp
import json
import uuid
from datetime import datetime

# Server configuration
BASE_URL = "http://localhost:8001"
TEST_HEADERS = {"Content-Type": "application/json"}

async def register_user(session, email, password, name):
    """Register a new user"""
    url = f"{BASE_URL}/api/v1/auth/register"
    user_data = {
        "email": email,
        "password": password,
        "full_name": name
    }
    
    async with session.post(url, json=user_data, headers=TEST_HEADERS) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Registered user: {email}")
            return data.get('access_token')
        else:
            error = await response.text()
            print(f"❌ Failed to register {email}: {error}")
            return None

async def login_user(session, email, password):
    """Login existing user"""
    url = f"{BASE_URL}/api/v1/auth/login"
    login_data = {
        "email": email,
        "password": password
    }
    
    async with session.post(url, json=login_data, headers=TEST_HEADERS) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Logged in user: {email}")
            return data.get('access_token')
        else:
            error = await response.text()
            print(f"❌ Failed to login {email}: {error}")
            return None

async def create_conversation(session, token, participant_emails):
    """Create a conversation between users"""
    url = f"{BASE_URL}/api/v1/messages/conversations"
    headers = {**TEST_HEADERS, "Authorization": f"Bearer {token}"}
    conversation_data = {
        "participant_emails": participant_emails,
        "title": f"Test Conversation {datetime.now().strftime('%H:%M:%S')}"
    }
    
    async with session.post(url, json=conversation_data, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Created conversation with {participant_emails}")
            return data.get('id')
        else:
            error = await response.text()
            print(f"❌ Failed to create conversation: {error}")
            return None

async def send_message(session, token, conversation_id, content):
    """Send a message in conversation"""
    url = f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages"
    headers = {**TEST_HEADERS, "Authorization": f"Bearer {token}"}
    message_data = {
        "content": content,
        "message_type": "text"
    }
    
    async with session.post(url, json=message_data, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Sent message: '{content}'")
            return data.get('id')
        else:
            error = await response.text()
            print(f"❌ Failed to send message: {error}")
            return None

async def get_conversations(session, token):
    """Get user's conversations"""
    url = f"{BASE_URL}/api/v1/messages/conversations"
    headers = {**TEST_HEADERS, "Authorization": f"Bearer {token}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Retrieved {len(data)} conversations")
            return data
        else:
            error = await response.text()
            print(f"❌ Failed to get conversations: {error}")
            return []

async def get_messages(session, token, conversation_id):
    """Get messages from conversation"""
    url = f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages"
    headers = {**TEST_HEADERS, "Authorization": f"Bearer {token}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            print(f"✅ Retrieved {len(data)} messages from conversation {conversation_id}")
            return data
        else:
            error = await response.text()
            print(f"❌ Failed to get messages: {error}")
            return []

async def test_security_violation(session, user1_token, user2_token, conversation_id):
    """Test if user2 can access user1's conversation data"""
    print("\n🔍 TESTING SECURITY: Can User2 access User1's conversation?")
    
    # User2 tries to get messages from User1's conversation
    url = f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages"
    headers = {**TEST_HEADERS, "Authorization": f"Bearer {user2_token}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            print(f"🚨 SECURITY BREACH: User2 accessed User1's conversation! Found {len(data)} messages")
            return True
        else:
            print(f"✅ SECURITY WORKING: User2 correctly blocked from User1's conversation")
            return False

async def main():
    """Run tangible user scenarios"""
    print("🚀 STARTING TANGIBLE USER SECURITY TESTS")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Create test users
        user1_email = f"test_user1_{uuid.uuid4().hex[:8]}@example.com"
        user2_email = f"test_user2_{uuid.uuid4().hex[:8]}@example.com"
        user3_email = f"test_user3_{uuid.uuid4().hex[:8]}@example.com"
        password = "securepassword123"
        
        # Register users
        user1_token = await register_user(session, user1_email, password, "Test User 1")
        user2_token = await register_user(session, user2_email, password, "Test User 2") 
        user3_token = await register_user(session, user3_email, password, "Test User 3")
        
        if not all([user1_token, user2_token, user3_token]):
            print("❌ User registration failed - stopping test")
            return
        
        print("\n" + "="*50)
        print("SCENARIO 1: User1 creates conversation with User2")
        print("="*50)
        
        # User1 creates conversation with User2
        conversation_id = await create_conversation(session, user1_token, [user2_email])
        
        if conversation_id:
            # User1 sends message
            await send_message(session, user1_token, conversation_id, "Hello User2, this is User1!")
            
            # User2 sends reply
            await send_message(session, user2_token, conversation_id, "Hi User1! Nice to meet you.")
            
            # Both users should see the conversation
            print("\n📋 User1's conversations:")
            user1_convos = await get_conversations(session, user1_token)
            
            print("\n📋 User2's conversations:")  
            user2_convos = await get_conversations(session, user2_token)
            
            print("\n📋 User3's conversations (should be empty):")
            user3_convos = await get_conversations(session, user3_token)
            
            print("\n" + "="*50)
            print("SCENARIO 2: Security Testing - User3 tries to access conversation")
            print("="*50)
            
            # Test security violation - User3 tries to access User1/User2 conversation
            security_breach = await test_security_violation(session, user1_token, user3_token, conversation_id)
            
            print("\n" + "="*50)
            print("SCENARIO 3: User3 creates separate conversation with User1")
            print("="*50)
            
            # User3 creates separate conversation with User1
            conversation2_id = await create_conversation(session, user3_token, [user1_email])
            if conversation2_id:
                await send_message(session, user3_token, conversation2_id, "Hello User1, this is User3!")
                await send_message(session, user1_token, conversation2_id, "Hi User3! I'm also talking with User2.")
                
                # Verify conversations are isolated
                print("\n🔍 FINAL CONVERSATION ISOLATION CHECK:")
                final_user1_convos = await get_conversations(session, user1_token)
                final_user2_convos = await get_conversations(session, user2_token) 
                final_user3_convos = await get_conversations(session, user3_token)
                
                print(f"User1 sees {len(final_user1_convos)} conversations (should be 2)")
                print(f"User2 sees {len(final_user2_convos)} conversations (should be 1)") 
                print(f"User3 sees {len(final_user3_convos)} conversations (should be 1)")
            
            print("\n" + "="*50)
            print("SECURITY ASSESSMENT SUMMARY:")
            print("="*50)
            if security_breach:
                print("🚨 CRITICAL: RLS NOT ENFORCED - Users can access others' conversations")
            else:
                print("✅ SECURE: RLS working - Users can only access their own conversations")
                
        else:
            print("❌ Conversation creation failed - cannot proceed with security tests")

if __name__ == "__main__":
    asyncio.run(main())
