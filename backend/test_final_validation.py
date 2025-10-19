import asyncio
import requests
import uuid

def test_final_validation():
    """Final validation of complete Phase 1"""
    print("🎯 FINAL PHASE 1 VALIDATION")
    
    # Generate unique test data
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"test_{unique_id}@example.com"
    test_username = f"user_{unique_id}"
    
    test_data = {
        'email': test_email,
        'username': test_username,
        'password': 'securepassword123',
        'full_name': f'Test User {unique_id}'
    }
    
    try:
        print("1. Testing new user registration...")
        response = requests.post(
            'http://localhost:8001/api/v1/auth/register',
            json=test_data,
            headers={'X-Timezone': 'Europe/London'}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print('✅ NEW USER REGISTRATION WORKING')
            print(f'   User ID: {user_data["id"]}')
            print(f'   Email: {user_data["email"]}')
            print(f'   Timezone: {user_data["timezone"]}')
            print(f'   Role: {user_data["role"]}')
        else:
            print(f'❌ Registration failed: {response.status_code} - {response.text}')
            return
        
        print("\n2. Testing login with new user...")
        login_data = {
            'email': test_email,
            'password': 'securepassword123'
        }
        response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print('✅ LOGIN WORKING')
            print(f'   Token type: {token_data["token_type"]}')
            print(f'   Token length: {len(token_data["access_token"])} chars')
        else:
            print(f'❌ Login failed: {response.status_code} - {response.text}')
            return
        
        print("\n3. Testing protected route with JWT...")
        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        response = requests.get('http://localhost:8001/api/v1/auth/me', headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print('✅ PROTECTED ROUTE WORKING')
            print(f'   User email: {user_info["email"]}')
            print(f'   Username: {user_info["username"]}')
            print(f'   Timezone: {user_info["timezone"]}')
        else:
            print(f'❌ Protected route failed: {response.status_code} - {response.text}')
            return
        
        print("\n4. Testing health endpoint...")
        response = requests.get('http://localhost:8001/api/v1/health')
        if response.status_code == 200:
            health_data = response.json()
            print('✅ HEALTH ENDPOINT WORKING')
            print(f'   Database: {health_data["database"]}')
            print(f'   Environment: {health_data["environment"]}')
        else:
            print(f'❌ Health check failed: {response.status_code}')
            return
        
        print("\n🎉 🎉 🎉 PHASE 1 COMPLETELY VALIDATED! 🎉 🎉 🎉")
        print("   Ready for PHASE 2: Core Platform Enhancement!")
        
    except Exception as e:
        print(f'❌ Final validation failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_validation()
