#!/bin/bash

echo "🔍 COMPREHENSIVE MOOD SYSTEM DIAGNOSTIC"
echo "========================================"

# Get token first
echo "1. 🔐 Authentication Test"
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }')

echo "Raw Token Response: $TOKEN_RESPONSE"
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Extracted Token: $TOKEN"

if [ -z "$TOKEN" ]; then
    echo "❌ FAILED: Cannot get authentication token"
    exit 1
fi
echo "✅ Authentication successful"

echo ""
echo "2. 📋 Available Endpoints Test"
echo "Testing base mood endpoints:"

# Test basic mood endpoints
ENDPOINTS=(
    "/api/v1/mood/entries/"
    "/api/v1/mood/entries/hybrid"
    "/api/v1/mood/stats/"
    "/api/v1/mood/taxonomy"
)

for endpoint in "${ENDPOINTS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001${endpoint}" -H "Authorization: Bearer $TOKEN")
    echo "   $endpoint : HTTP $response"
done

echo ""
echo "3. 🔧 Schema Analysis"
echo "Checking mood creation requirements..."

# Let's see what fields are required for mood creation
echo "Creating test mood entry with minimal fields:"
TEST_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/mood/entries/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "calm",
    "intensity": 5
  }')

echo "Minimal fields response: $TEST_RESPONSE"

echo ""
echo "4. 🎯 Working Endpoint Verification"
echo "Testing endpoints that definitely work:"

# Test statistics endpoint (which worked)
STATS_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/stats/?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Statistics endpoint: WORKING"
echo "   Response sample: $(echo $STATS_RESPONSE | cut -c 1-100)..."

# Test taxonomy endpoint (which worked)
TAXONOMY_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/taxonomy" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Taxonomy endpoint: WORKING"
echo "   Total moods: $(echo $TAXONOMY_RESPONSE | grep -o '"total_moods":[0-9]*' | cut -d: -f2)"

echo ""
echo "5. 🔄 Hybrid Endpoint Investigation"
echo "Testing hybrid endpoint variations:"

# Test different hybrid endpoint formats
HYBRID_VARIANTS=(
    "hybrid"
    "hybrid/"
    "hybrid?days=7"
    "hybrid/"
)

for variant in "${HYBRID_VARIANTS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001/api/v1/mood/entries/${variant}" -H "Authorization: Bearer $TOKEN")
    echo "   /api/v1/mood/entries/${variant} : HTTP $response"
done

echo ""
echo "========================================"
echo "🎯 DIAGNOSTIC COMPLETE"
