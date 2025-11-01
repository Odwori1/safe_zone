#!/bin/bash
echo "🧪 TESTING CRISIS SYSTEM WITH RLS FIX"
echo "======================================"

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Testing crisis endpoints..."

# Test creating data through API (should work if backend sets RLS context)
echo -e "\n1. 📝 CREATE CRISIS PREFERENCES VIA API"
curl -s -X POST "http://localhost:8001/api/v1/crisis-support/preferences/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "en",
    "country_code": "US",
    "consent_to_contact": true
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'user_id' in data:
        print('   ✅ SUCCESS: API created preferences with RLS')
    else:
        print('   ❌ FAILED: API cannot create (RLS blocking)')
        print('   Response:', data.get('detail', 'Unknown error'))
except Exception as e:
    print('   ❌ ERROR:', e)
"

# Test reading data
echo -e "\n2. 📊 CHECKING DATA VIA API"
endpoints=("preferences" "emergency-contacts" "safety-plans" "wellness-checkins" "crisis-alerts")
for endpoint in "${endpoints[@]}"; do
    count=$(curl -s -X GET "http://localhost:8001/api/v1/crisis-support/${endpoint}/" \
      -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'total' in data:
        print(data['total'])
    elif 'id' in data:
        print('1')
    else:
        print('0')
except:
    print('0')
")
    echo "   ${endpoint}: $count records"
done

echo -e "\n🎯 TEST COMPLETE"
