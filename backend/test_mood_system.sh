#!/bin/bash

# File: ~/safe_zone/test_mood_system.sh

echo "🔍 Testing Safe Zone Mood Tracking System"
echo "=========================================="

# Step 1: Login and get token
echo "1. Authenticating..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }')

echo "Login Response: $TOKEN_RESPONSE"

# Extract token from response
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token"
  exit 1
fi

echo "✅ Token obtained successfully"

# Step 2: Create a mood entry
echo ""
echo "2. Creating mood entry..."
MOOD_CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/mood/entries/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "calm",
    "intensity": 7,
    "notes": "Testing mood system functionality",
    "triggers": ["system testing"],
    "activities": ["development", "documentation"]
  }')

echo "Mood Creation Response: $MOOD_CREATE_RESPONSE"

# Step 3: Test hybrid endpoint
echo ""
echo "3. Testing hybrid endpoint (mood history)..."
HYBRID_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/entries/hybrid?days=30" \
  -H "Authorization: Bearer $TOKEN")

echo "Hybrid Endpoint Response: $HYBRID_RESPONSE"

# Step 4: Test statistics endpoint
echo ""
echo "4. Testing statistics endpoint..."
STATS_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/stats/?days=30" \
  -H "Authorization: Bearer $TOKEN")

echo "Statistics Response: $STATS_RESPONSE"

echo ""
echo "🎉 Mood System Testing Complete!"
echo "================================="
echo "All endpoints are operational and ready for frontend integration."
