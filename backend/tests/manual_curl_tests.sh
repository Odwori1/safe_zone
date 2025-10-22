#!/bin/bash
echo "🔍 MANUAL CURL TESTS FOR MESSAGING SECURITY"
echo "=========================================="

# Base URL
BASE_URL="http://localhost:8001"

# Create unique test users
USER1_EMAIL="curl_user1_$(date +%s)@example.com"
USER2_EMAIL="curl_user2_$(date +%s)@example.com" 
USER3_EMAIL="curl_user3_$(date +%s)@example.com"
PASSWORD="securepassword123"

echo "📝 Test Users:"
echo "User 1: $USER1_EMAIL"
echo "User 2: $USER2_EMAIL" 
echo "User 3: $USER3_EMAIL"
echo ""

# Function to make JSON requests
json_request() {
    local method=$1
    local url=$2
    local token=$3
    local data=$4
    
    if [ -n "$token" ]; then
        AUTH_HEADER="Authorization: Bearer $token"
    else
        AUTH_HEADER=""
    fi
    
    if [ -n "$data" ]; then
        curl -s -X $method "$url" \
            -H "Content-Type: application/json" \
            -H "$AUTH_HEADER" \
            -d "$data"
    else
        curl -s -X $method "$url" \
            -H "Content-Type: application/json" \
            -H "$AUTH_HEADER"
    fi
}

echo "1. REGISTERING TEST USERS"
echo "-------------------------"

# Register User 1
echo "Registering User 1..."
USER1_TOKEN=$(json_request "POST" "$BASE_URL/api/v1/auth/register" "" "{\"email\": \"$USER1_EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"CURL User 1\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "User 1 Token: ${USER1_TOKEN:0:20}..."

# Register User 2  
echo "Registering User 2..."
USER2_TOKEN=$(json_request "POST" "$BASE_URL/api/v1/auth/register" "" "{\"email\": \"$USER2_EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"CURL User 2\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "User 2 Token: ${USER2_TOKEN:0:20}..."

# Register User 3
echo "Registering User 3..."
USER3_TOKEN=$(json_request "POST" "$BASE_URL/api/v1/auth/register" "" "{\"email\": \"$USER3_EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"CURL User 3\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "User 3 Token: ${USER3_TOKEN:0:20}..."

echo ""
echo "2. TESTING CONVERSATION CREATION"
echo "-------------------------------"

# User 1 creates conversation with User 2
echo "User 1 creating conversation with User 2..."
CONVERSATION_RESPONSE=$(json_request "POST" "$BASE_URL/api/v1/messages/conversations" "$USER1_TOKEN" "{\"participant_emails\": [\"$USER2_EMAIL\"], \"title\": \"CURL Test Conversation\"}")
echo "Conversation Response: $CONVERSATION_RESPONSE"

# Extract conversation ID
CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Conversation ID: $CONVERSATION_ID"

echo ""
echo "3. TESTING MESSAGE EXCHANGE"
echo "--------------------------"

# User 1 sends message
echo "User 1 sending message..."
MESSAGE1_RESPONSE=$(json_request "POST" "$BASE_URL/api/v1/messages/conversations/$CONVERSATION_ID/messages" "$USER1_TOKEN" "{\"content\": \"Hello User 2 from CURL test!\", \"message_type\": \"text\"}")
echo "Message 1 Response: $MESSAGE1_RESPONSE"

# User 2 sends reply
echo "User 2 sending reply..."
MESSAGE2_RESPONSE=$(json_request "POST" "$BASE_URL/api/v1/messages/conversations/$CONVERSATION_ID/messages" "$USER2_TOKEN" "{\"content\": \"Hello User 1! CURL test working.\", \"message_type\": \"text\"}")
echo "Message 2 Response: $MESSAGE2_RESPONSE"

echo ""
echo "4. TESTING SECURITY - USER 3 ACCESS ATTEMPT"
echo "------------------------------------------"

# User 3 tries to get the conversation (should fail)
echo "User 3 trying to access conversation (should fail)..."
USER3_ACCESS_RESPONSE=$(json_request "GET" "$BASE_URL/api/v1/messages/conversations/$CONVERSATION_ID/messages" "$USER3_TOKEN")
echo "User 3 Access Response: $USER3_ACCESS_RESPONSE"

# User 3 tries to send message (should fail)
echo "User 3 trying to send message (should fail)..."
USER3_SEND_RESPONSE=$(json_request "POST" "$BASE_URL/api/v1/messages/conversations/$CONVERSATION_ID/messages" "$USER3_TOKEN" "{\"content\": \"I should not be able to send this\", \"message_type\": \"text\"}")
echo "User 3 Send Response: $USER3_SEND_RESPONSE"

echo ""
echo "5. VERIFYING USER ACCESS"
echo "-----------------------"

# User 1 should see conversations
echo "User 1 conversations:"
USER1_CONVOS=$(json_request "GET" "$BASE_URL/api/v1/messages/conversations" "$USER1_TOKEN")
echo "$USER1_CONVOS" | python3 -m json.tool

# User 2 should see conversations  
echo "User 2 conversations:"
USER2_CONVOS=$(json_request "GET" "$BASE_URL/api/v1/messages/conversations" "$USER2_TOKEN")
echo "$USER2_CONVOS" | python3 -m json.tool

# User 3 should see NO conversations
echo "User 3 conversations (should be empty):"
USER3_CONVOS=$(json_request "GET" "$BASE_URL/api/v1/messages/conversations" "$USER3_TOKEN")
echo "$USER3_CONVOS" | python3 -m json.tool

echo ""
echo "🎯 SECURITY ASSESSMENT:"
echo "======================"

if echo "$USER3_ACCESS_RESPONSE" | grep -q "error\|Not Found\|Forbidden"; then
    echo "✅ SECURITY WORKING: User 3 correctly blocked from accessing conversation"
else
    echo "🚨 SECURITY BREACH: User 3 was able to access the conversation!"
fi

if echo "$USER3_SEND_RESPONSE" | grep -q "error\|Not Found\|Forbidden"; then
    echo "✅ SECURITY WORKING: User 3 correctly blocked from sending messages"
else
    echo "🚨 SECURITY BREACH: User 3 was able to send messages!"
fi

echo ""
echo "Test completed. Check above for security assessment."
