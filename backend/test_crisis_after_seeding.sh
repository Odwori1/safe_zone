#!/bin/bash
echo "🧪 TESTING CRISIS SYSTEM AFTER SEEDING"
echo "======================================"

# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer_test@example.com",
    "password": "DeveloperPass123!"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Testing seeded crisis data..."

# Test all endpoints
endpoints=("resources" "preferences" "emergency-contacts" "safety-plans" "wellness-checkins" "crisis-alerts")

for endpoint in "${endpoints[@]}"; do
    echo -e "\n📋 Testing /crisis-support/${endpoint}/"
    response=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8001/api/v1/crisis-support/${endpoint}/")
    
    if echo "$response" | grep -q "error\|detail"; then
        echo "   ❌ Error: $response"
    else
        # Parse the response to show meaningful info
        case $endpoint in
            "resources")
                count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('resources', [])))")
                echo "   ✅ $count crisis resources"
                ;;
            "preferences")
                lang=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('preferred_language', 'N/A'))")
                echo "   ✅ Preferences found (Language: $lang)"
                ;;
            "emergency-contacts")
                count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))")
                primary=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Yes' if data.get('has_primary') else 'No')")
                echo "   ✅ $count contacts (Primary: $primary)"
                ;;
            "safety-plans")
                count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))")
                active=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Yes' if data.get('active_plan') else 'No')")
                echo "   ✅ $count safety plans (Active: $active)"
                ;;
            "wellness-checkins")
                count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))")
                today=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print('Yes' if data.get('today_checkin') else 'No')")
                echo "   ✅ $count checkins (Today: $today)"
                ;;
            "crisis-alerts")
                count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))")
                active=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('active_alerts', [])))")
                echo "   ✅ $count alerts (Active: $active)"
                ;;
        esac
    fi
done

echo -e "\n🎯 CRISIS SYSTEM TEST COMPLETE"
