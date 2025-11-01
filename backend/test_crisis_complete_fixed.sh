#!/bin/bash
echo "🚀 COMPLETE CRISIS SYSTEM TEST (FIXED)"
echo "======================================"

# Get token
echo "Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token obtained"

# Test functions with better error handling
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -e "\n$name"
    echo "URL: $endpoint"
    
    if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
        response=$(curl -s -X $method "http://localhost:8001/api/v1/crisis-support/$endpoint" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "$data")
    else
        response=$(curl -s -X $method "http://localhost:8001/api/v1/crisis-support/$endpoint" \
          -H "Authorization: Bearer $TOKEN")
    fi
    
    # Check if response contains error or success indicators
    if echo "$response" | grep -q "detail"; then
        if echo "$response" | grep -q "already exist"; then
            echo "✅ Already exists (this is fine)"
        elif echo "$response" | grep -q "duplicate"; then
            echo "✅ Already exists (duplicate)"
        else
            echo "❌ Error: $response"
        fi
    elif echo "$response" | grep -q "\"id\""; then
        echo "✅ Created successfully"
    elif echo "$response" | grep -q "\"user_id\""; then
        echo "✅ Created successfully" 
    else
        echo "⚠️  Response: $response"
    fi
}

# Test 1: Get crisis resources
test_endpoint "1. GET CRISIS RESOURCES" "GET" "resources/"

# Test 2: Create or update crisis preferences
test_endpoint "2. CREATE CRISIS PREFERENCES" "POST" "preferences/" '{
    "preferred_language": "en",
    "country_code": "US",
    "consent_to_contact": true
}'

# If creation failed, try update
if echo "$response" | grep -q "already exist\|duplicate"; then
    test_endpoint "2b. UPDATE CRISIS PREFERENCES" "PUT" "preferences/" '{
        "preferred_language": "en",
        "country_code": "US", 
        "consent_to_contact": true
    }'
fi

# Test 3: Create emergency contact
test_endpoint "3. CREATE EMERGENCY CONTACT" "POST" "emergency-contacts/" '{
    "name": "Sarah Wilson",
    "relationship": "Sister",
    "phone_number": "+1-555-0101",
    "is_primary": true
}'

# Test 4: Create safety plan (using actual schema)
test_endpoint "4. CREATE SAFETY PLAN" "POST" "safety-plans/" '{
    "plan_name": "My Safety Plan",
    "personal_warning_signs": ["Feeling overwhelmed", "Sleeping too much"],
    "internal_coping_strategies": ["Deep breathing", "Journaling"],
    "social_coping_strategies": ["Call a friend", "Visit family"],
    "crisis_line_preferences": ["988", "Crisis Text Line"]
}'

# Test 5: Create wellness checkin
test_endpoint "5. CREATE WELLNESS CHECKIN" "POST" "wellness-checkins/" '{
    "checkin_date": "2025-11-01",
    "mood_rating": 6,
    "anxiety_level": 4
}'

# Test 6: Create crisis alert
test_endpoint "6. CREATE CRISIS ALERT" "POST" "crisis-alerts/" '{
    "alert_type": "safety_concern",
    "severity_level": "medium",
    "message": "Need support with anxiety",
    "location_data": {"city": "Seattle", "country": "US"}
}'

# Test 7: Verify all data
echo -e "\n7. VERIFYING ALL DATA"
endpoints=("preferences/" "emergency-contacts/" "safety-plans/" "wellness-checkins/" "crisis-alerts/")

for endpoint in "${endpoints[@]}"; do
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
        print('1' if 'id' in data else '0')
except:
    print('0')
")
    echo "  $endpoint: $count records"
done

echo -e "\n🎉 CRISIS SYSTEM TEST COMPLETED!"
