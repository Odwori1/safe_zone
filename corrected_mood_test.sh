#!/bin/bash

echo "🎯 CORRECTED MOOD SYSTEM TEST"
echo "=============================="

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."

echo ""
echo "1. ✅ TEST WORKING ENDPOINTS"

echo "   📊 Statistics:"
STATS=$(curl -s -X GET "http://localhost:8001/api/v1/mood/stats/?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "   - Total entries: $(echo $STATS | grep -o '"total_entries":[0-9]*' | cut -d: -f2)"
echo "   - Avg intensity: $(echo $STATS | grep -o '"average_intensity":[0-9.]*' | cut -d: -f2)"

echo ""
echo "   📚 Taxonomy:"
TAXONOMY=$(curl -s -X GET "http://localhost:8001/api/v1/mood/taxonomy" \
  -H "Authorization: Bearer $TOKEN")
echo "   - Total moods: $(echo $TAXONOMY | grep -o '"total_moods":[0-9]*' | cut -d: -f2)"
echo "   - Categories: $(echo $TAXONOMY | grep -o '"categories":{[^}]*' | head -1)"

echo ""
echo "2. 🔧 TEST MOOD CREATION (Fixed)"

# Try different creation formats
echo "   Testing mood creation formats..."

# Format 1: Minimal required fields
echo "   Format 1 - Minimal:"
RESPONSE1=$(curl -s -X POST "http://localhost:8001/api/v1/mood/entries/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "calm",
    "intensity": 6
  }')
echo "   Result: $(echo $RESPONSE1 | grep -o '"detail":"[^"]*' | cut -d'"' -f4 || echo "Unknown response")"

# Format 2: With all optional fields
echo "   Format 2 - Full:"
RESPONSE2=$(curl -s -X POST "http://localhost:8001/api/v1/mood/entries/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mood": "grateful",
    "intensity": 8,
    "notes": "Test mood entry with all fields",
    "triggers": ["testing", "development"],
    "activities": ["coding", "documentation"],
    "physical_symptoms": []
  }')
echo "   Result: $(echo $RESPONSE2 | grep -o '"mood":"[^"]*' | cut -d'"' -f4 || echo "Unknown response")"

echo ""
echo "3. 🔍 CHECK EXACT HYBRID ENDPOINT"

# Test exact hybrid endpoint from routes
HYBRID_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/entries/hybrid?days=7" \
  -H "Authorization: Bearer $TOKEN")
HYBRID_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8001/api/v1/mood/entries/hybrid?days=7" -H "Authorization: Bearer $TOKEN")

echo "   Hybrid endpoint status: HTTP $HYBRID_STATUS"
if [ "$HYBRID_STATUS" = "200" ]; then
    echo "   ✅ Hybrid endpoint: WORKING"
    echo "   Entries found: $(echo $HYBRID_RESPONSE | grep -o '"entries":\[[^]]*' | wc -l)"
else
    echo "   ❌ Hybrid endpoint: NOT WORKING"
    echo "   Response: $HYBRID_RESPONSE"
fi

echo ""
echo "4. 📋 LIST ALL MOOD ENTRIES"
ENTRIES_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/mood/entries/?limit=5" \
  -H "Authorization: Bearer $TOKEN")
ENTRIES_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8001/api/v1/mood/entries/?limit=5" -H "Authorization: Bearer $TOKEN")

echo "   Entries endpoint status: HTTP $ENTRIES_STATUS"
if [ "$ENTRIES_STATUS" = "200" ]; then
    echo "   ✅ Entries endpoint: WORKING"
else
    echo "   ❌ Entries endpoint: NOT WORKING"
fi

echo ""
echo "=============================="
echo "🎯 TEST COMPLETE"
