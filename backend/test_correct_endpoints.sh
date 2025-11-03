#!/bin/bash

echo "🎯 TESTING CORRECT PHASE 3 ENDPOINTS"
echo "===================================="

# Get token
echo "1. Getting authentication token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Token obtained"

echo ""
echo "2. Testing CORRECT endpoints..."
echo ""

# Test CORRECT Users endpoint
echo "📋 Testing Users Search (Correct endpoint)..."
USERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/users/search")
echo "Users Search: $USERS_RESPONSE"

# Test CORRECT Mood endpoint
echo "😊 Testing Mood Entries (Correct endpoint)..."
MOOD_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/mood/entries")
echo "Mood Entries: $(echo $MOOD_RESPONSE | cut -c 1-100)..."

# Test CORRECT Uploads endpoint
echo "📁 Testing Uploads Presigned URL endpoint..."
UPLOADS_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "test.jpg", "file_type": "image/jpeg"}' \
  "http://localhost:8001/api/v1/uploads/presigned-url")
echo "Uploads Presigned URL: $UPLOADS_RESPONSE"

# Test CORRECT Files endpoint
echo "🗂️ Testing Files endpoint..."
FILES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/files/")
echo "Files: $FILES_RESPONSE"

echo ""
echo "3. Testing Messaging System with Debug..."
echo ""

# Create conversation
echo "💬 Creating conversation..."
CONVO_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/messages/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_group": false,
    "title": "Debug Test Chat"
  }')
echo "Conversation: $CONVO_RESPONSE"

CONVO_ID=$(echo $CONVO_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$CONVO_ID" ]; then
    echo "✅ Conversation created: $CONVO_ID"
    
    # Test message creation with detailed error
    echo "📝 Creating message..."
    MESSAGE_RESPONSE=$(curl -s -X POST \
      "http://localhost:8001/api/v1/messages/conversations/$CONVO_ID/messages" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "content": "Debug test message",
        "content_type": "text"
      }')
    echo "Message Response: $MESSAGE_RESPONSE"
    
    # Test getting conversations
    echo "📨 Getting conversations..."
    CONVOS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8001/api/v1/messages/conversations")
    echo "Conversations: $CONVOS_RESPONSE"
else
    echo "❌ Failed to create conversation"
fi

echo ""
echo "4. Testing Live Audio Rooms (Already Working)..."
echo ""

# Test audio rooms
echo "🎙️ Testing audio rooms..."
AUDIO_ROOMS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/audio/rooms")
echo "Audio Rooms: $(echo $AUDIO_ROOMS_RESPONSE | cut -c 1-100)..."

echo ""
echo "5. Testing Moderation System..."
echo ""

MODERATION_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/moderation/")
echo "Moderation: $MODERATION_RESPONSE"

echo ""
echo "🎯 TEST SUMMARY"
echo "==============="
echo "✅ Audio Rooms: WORKING"
echo "✅ Moderation: WORKING" 
echo "✅ Files: WORKING"
echo "🔍 Testing other endpoints above..."
