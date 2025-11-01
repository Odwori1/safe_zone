import requests
import json

# Get a fresh token
login_data = {
    "email": "developer_test@example.com", 
    "password": "DeveloperPass123!"
}

login_response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data)
token = login_response.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

print("🔍 Debugging Search Endpoint...")
try:
    response = requests.get(
        "http://localhost:8001/api/v1/crisis-support/resources/search/?q=suicide",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print("❌ Server Error 500")
        try:
            error_detail = response.json()
            print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
