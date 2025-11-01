import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ODA4OTU2Yi0xMWZiLTQyNTMtOTFlZi05OGI5OTAyZmZiYzgiLCJlbWFpbCI6ImRldmVsb3Blcl90ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzYxOTk5NTMxfQ.f2C75y80KLjnaCM2osPFjXLrSc4JQG7EN3_cMjNJyzU"

headers = {"Authorization": f"Bearer {token}"}

print("🔍 Testing Crisis Resources Endpoint with correct URL...")

# Test the correct endpoint
url = "http://localhost:8001/api/v1/crisis-support/resources/"
print(f"Testing URL: {url}")

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print("❌ Server Error 500")
        try:
            error_detail = response.json()
            print(f"Error Detail: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
    elif response.status_code == 200:
        print("✅ Success!")
        data = response.json()
        print(f"Found {data.get('total', 0)} resources")
        if data.get('resources'):
            print("Sample resource:", data['resources'][0])
    else:
        print(f"Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
