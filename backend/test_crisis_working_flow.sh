#!/bin/bash
echo "🚀 WORKING CRISIS SYSTEM FLOW TEST"
echo "==================================="

# Get token
echo "Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtained"

# Test 1: Get crisis resources (should work)
echo -e "\n=== 1. GET CRISIS RESOURCES ==="
curl -s -X GET "http://localhost:8001/api/v1/crisis-support/resources/" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'✅ Resources found: {len(data.get(\\\"resources\\\", []))}')
"

# Test 2: Create crisis preferences (simplified)
echo -e "\n=== 2. CREATE CRISIS PREFERENCES ==="
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
        print('✅ Preferences created successfully')
    else:
        print('❌ Failed to create preferences')
        print(data)
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 3: Create emergency contact (simplified)
echo -e "\n=== 3. CREATE EMERGENCY CONTACT ==="
curl -s -X POST "http://localhost:8001/api/v1/crisis-support/emergency-contacts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Contact",
    "relationship": "Friend",
    "phone_number": "+1-555-0001",
    "is_primary": true
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'id' in data:
        print('✅ Emergency contact created successfully')
        print(f'Contact ID: {data[\\\"id\\\"]}')
    else:
        print('❌ Failed to create contact')
        print(data)
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 4: Create safety plan (using actual schema)
echo -e "\n=== 4. CREATE SAFETY PLAN ==="
curl -s -X POST "http://localhost:8001/api/v1/crisis-support/safety-plans/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "Test Safety Plan"
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'id' in data:
        print('✅ Safety plan created successfully')
    else:
        print('❌ Failed to create safety plan')
        print(data)
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 5: Create wellness checkin (simplified)
echo -e "\n=== 5. CREATE WELLNESS CHECKIN ==="
curl -s -X POST "http://localhost:8001/api/v1/crisis-support/wellness-checkins/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "checkin_date": "2025-11-01",
    "mood_rating": 5
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'id' in data:
        print('✅ Wellness checkin created successfully')
    else:
        print('❌ Failed to create wellness checkin')
        print(data)
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 6: Create crisis alert (with proper JSON string)
echo -e "\n=== 6. CREATE CRISIS ALERT ==="
curl -s -X POST "http://localhost:8001/api/v1/crisis-support/crisis-alerts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "safety_concern",
    "severity_level": "medium",
    "message": "Test alert message",
    "location_data": "{\"city\": \"Seattle\", \"country\": \"US\"}"
  }' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'id' in data:
        print('✅ Crisis alert created successfully')
    else:
        print('❌ Failed to create crisis alert')
        print(data)
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test 7: Verify all data
echo -e "\n=== 7. VERIFY ALL DATA ==="
endpoints=("preferences/" "emergency-contacts/" "safety-plans/" "wellness-checkins/" "crisis-alerts/")

for endpoint in "${endpoints[@]}"; do
    echo -n "Checking $endpoint... "
    count=$(curl -s -X GET "http://localhost:8001/api/v1/crisis-support/$endpoint" \
      -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'total' in data:
        print(data['total'])
    elif isinstance(data, list):
        print(len(data))
    else:
        print('0')
except:
    print('error')
")
    echo "Found: $count"
done

echo -e "\n🎉 TEST COMPLETED!"
