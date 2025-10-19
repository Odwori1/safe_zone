import asyncio
import requests
import json

def test_auth_system():
    print('🔐 TESTING AUTHENTICATION SYSTEM')
    
    # Test registration
    reg_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'securepassword123',
        'full_name': 'Test User'
    }
    
    try:
        # Register user
        print("1. Testing user registration...")
        response = requests.post(
            'http://localhost:8001/api/v1/auth/register',
            json=reg_data,
            headers={'X-Timezone': 'America/New_York'}  # Test timezone detection
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print('✅ User registration working')
            print(f'✅ User created with ID: {user_data["id"]}')
            print(f'✅ Timezone detected: {user_data["timezone"]}')
            print(f'✅ User role: {user_data["role"]}')
        else:
            print(f'⚠️ Registration response: {response.status_code} - {response.text}')
        
        # Test login
        print("\n2. Testing user login...")
        login_data = {
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print('✅ User login working')
            print(f'✅ JWT token received: {len(token_data["access_token"])} chars')
            print(f'✅ Token type: {token_data["token_type"]}')
            print(f'✅ Expires in: {token_data["expires_in"]} seconds')
            
            # Test protected route
            print("\n3. Testing protected route...")
            headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
            response = requests.get('http://localhost:8001/api/v1/auth/me', headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                print('✅ Protected route working')
                print(f'✅ User email: {user_info["email"]}')
                print(f'✅ User role: {user_info["role"]}')
            else:
                print(f'⚠️ Protected route response: {response.status_code} - {response.text}')
                
        else:
            print(f'⚠️ Login response: {response.status_code} - {response.text}')
            
    except Exception as e:
        print(f'❌ Auth test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_system()
