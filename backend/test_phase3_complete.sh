#!/bin/bash

echo "=== PHASE 3 COMPREHENSIVE TESTING ==="
echo "Testing with existing user: developer_test@example.com"
echo ""

# Step 1: Authentication
echo "1. 🔐 AUTHENTICATION TEST"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }')

echo "Login Response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ LOGIN FAILED - Cannot proceed"
  exit 1
fi

echo "✅ Login Successful - Token Received"
echo "Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Test Core Features First
echo "2. 🏗️ CORE FEATURES VERIFICATION"
echo "Testing posts..."
POSTS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/posts")
echo "Posts API: $(echo $POSTS_RESPONSE | cut -c 1-100)..."

echo "Testing users..."
USERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/users")
echo "Users API: $(echo $USERS_RESPONSE | cut -c 1-100)..."

echo "Testing mood..."
MOOD_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/mood")
echo "Mood API: $(echo $MOOD_RESPONSE | cut -c 1-100)..."
echo ""

# Step 3: Live Audio Rooms Test
echo "3. 🎙️ LIVE AUDIO ROOMS TEST"
echo "Creating audio room..."
AUDIO_ROOM_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/audio/rooms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Phase 3 Audio Test Room",
    "description": "Testing the live audio rooms feature",
    "visibility": "public",
    "max_participants": 5,
    "room_type": "support"
  }')

echo "Audio Room Creation: $AUDIO_ROOM_RESPONSE"

ROOM_ID=$(echo $AUDIO_ROOM_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$ROOM_ID" ]; then
  echo "✅ Audio Room Created - ID: $ROOM_ID"
  
  # Test getting the room
  echo "Retrieving audio room..."
  GET_ROOM_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8001/api/v1/audio/rooms/$ROOM_ID")
  echo "Room Retrieved: $(echo $GET_ROOM_RESPONSE | cut -c 1-100)..."
  
  # Test getting all rooms
  echo "Retrieving all audio rooms..."
  ALL_ROOMS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8001/api/v1/audio/rooms")
  echo "All Rooms: $(echo $ALL_ROOMS_RESPONSE | cut -c 1-100)..."
else
  echo "❌ Audio Room Creation Failed"
fi
echo ""

# Step 4: Messaging System Test
echo "4. 💬 MESSAGING SYSTEM TEST"
echo "Creating conversation..."
CONVO_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/messages/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_group": false,
    "title": "Phase 3 Test Chat"
  }')

echo "Conversation Creation: $CONVO_RESPONSE"

CONVO_ID=$(echo $CONVO_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$CONVO_ID" ]; then
  echo "✅ Conversation Created - ID: $CONVO_ID"
  
  # Test creating message
  echo "Creating test message..."
  MESSAGE_RESPONSE=$(curl -s -X POST \
    "http://localhost:8001/api/v1/messages/conversations/$CONVO_ID/messages" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "content": "Testing Phase 3 messaging system - this is working!",
      "content_type": "text"
    }')
  
  echo "Message Creation: $MESSAGE_RESPONSE"
  
  # Test getting conversations
  echo "Getting user conversations..."
  USER_CONVOS=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8001/api/v1/messages/conversations")
  echo "User Conversations Retrieved: $(echo $USER_CONVOS | cut -c 1-100)..."
else
  echo "❌ Conversation Creation Failed"
fi
echo ""

# Step 5: File Upload System Test
echo "5. 📁 FILE UPLOAD SYSTEM TEST"
echo "Testing files endpoint..."
FILES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/files/")
echo "Files Endpoint: $FILES_RESPONSE"

echo "Testing uploads endpoint..."
UPLOADS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/uploads/files")
echo "Uploads Endpoint: $UPLOADS_RESPONSE"
echo ""

# Step 6: Moderation System Test
echo "6. 🛡️ MODERATION SYSTEM TEST"
echo "Testing moderation endpoint..."
MODERATION_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/moderation/")
echo "Moderation Endpoint: $MODERATION_RESPONSE"
echo ""

# Final Summary
echo "=== TESTING COMPLETE ==="
echo "✅ Phase 3 Backend Endpoints Tested"
echo "🎯 Ready for Frontend Integration"
echo ""
echo "NEXT STEPS:"
echo "1. Review all test results above"
echo "2. Check for any error messages"
echo "3. Proceed to frontend integration"
