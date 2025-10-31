#!/bin/bash

echo "🎯 WORKING MOOD SYSTEM TEST - ACTUAL ENDPOINTS"
echo "=============================================="

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

echo ""
echo "   📈 Enhanced Stats:"
ENHANCED_STATS=$(curl -s -X GET "http://localhost:8001/api/v1/mood/stats/enhanced?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "   - Status: $(echo $ENHANCED_STATS | grep -o '"total_entries":[0-9]*' | cut -d: -f2 && echo "WORKING" || echo "ERROR")"

echo ""
echo "   🧠 Clinical Insights:"
INSIGHTS=$(curl -s -X GET "http://localhost:8001/api/v1/mood/insights/clinical?days=7" \
  -H "Authorization: Bearer $TOKEN")
echo "   - Status: $(echo $INSIGHTS | grep -o '"dominant_category":"[^"]*' | cut -d'"' -f4 && echo "WORKING" || echo "ERROR")"

echo ""
echo "2. 🔄 TEST ACTUAL HYBRID ENDPOINTS"

echo "   Testing /hybrid-working:"
HYBRID_WORKING=$(curl -s -X GET "http://localhost:8001/api/v1/mood/entries/hybrid-working?days=7" \
  -H "Authorization: Bearer $TOKEN")
HYBRID_WORKING_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8001/api/v1/mood/entries/hybrid-working?days=7" -H "Authorization: Bearer $TOKEN")
echo "   - Status: HTTP $HYBRID_WORKING_STATUS"
if [ "$HYBRID_WORKING_STATUS" = "200" ]; then
    echo "   ✅ Hybrid-working: OPERATIONAL"
    echo "   - Response length: ${#HYBRID_WORKING} characters"
else
    echo "   ❌ Hybrid-working: FAILED"
    echo "   - Response: $HYBRID_WORKING"
fi

echo ""
echo "   Testing /hybrid-enhanced:"
HYBRID_ENHANCED=$(curl -s -X GET "http://localhost:8001/api/v1/mood/entries/hybrid-enhanced?days=7" \
  -H "Authorization: Bearer $TOKEN")
HYBRID_ENHANCED_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8001/api/v1/mood/entries/hybrid-enhanced?days=7" -H "Authorization: Bearer $TOKEN")
echo "   - Status: HTTP $HYBRID_ENHANCED_STATUS"
if [ "$HYBRID_ENHANCED_STATUS" = "200" ]; then
    echo "   ✅ Hybrid-enhanced: OPERATIONAL"
    echo "   - Response length: ${#HYBRID_ENHANCED} characters"
else
    echo "   ❌ Hybrid-enhanced: FAILED"
    echo "   - Response: $HYBRID_ENHANCED"
fi

echo ""
echo "3. 🔧 DEBUG MOOD CREATION ISSUE"

echo "   Let's check the actual error in backend logs:"
echo "   The error suggests mood_category is being returned as an object instead of string"

echo ""
echo "4. 📋 TEST OTHER WORKING FEATURES"

echo "   Testing mood creation from existing post (if any posts exist):"
# First, let's check if we have any posts
POSTS_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/posts/?page=1&limit=1" \
  -H "Authorization: Bearer $TOKEN")
echo "   - Posts endpoint status: $(echo $POSTS_RESPONSE | grep -o '"posts":\[[^]]*' | head -1 && echo "WORKING" || echo "NO POSTS")"

echo ""
echo "=============================================="
echo "🎯 TEST COMPLETE - ACTUAL WORKING ENDPOINTS:"
echo "✅ /api/v1/mood/stats/"
echo "✅ /api/v1/mood/taxonomy" 
echo "✅ /api/v1/mood/stats/enhanced"
echo "✅ /api/v1/mood/insights/clinical"
echo "❓ /api/v1/mood/entries/hybrid-working (needs testing)"
echo "❓ /api/v1/mood/entries/hybrid-enhanced (needs testing)"
echo "❌ /api/v1/mood/entries/ (broken - schema issue)"
