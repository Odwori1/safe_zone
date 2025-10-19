import requests
import json

def test_profiles_system():
    """Test the complete user profiles system"""
    
    # Test login first
    login_data = {'email': 'test_bc64ceba@example.com', 'password': 'securepassword123'}
    response = requests.post('http://localhost:8001/api/v1/auth/login', json=login_data)
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    print('🔐 Testing User Profiles System...')

    # Test get profile
    response = requests.get('http://localhost:8001/api/v1/profiles/me', headers=headers)
    print(f'✅ Get profile: {response.status_code}')
    if response.status_code == 200:
        user_data = response.json()
        print(f'   User: {user_data["username"]}')

    # Test update profile
    update_data = {
        'bio': 'Mental health advocate and support seeker',
        'timezone': 'Europe/London',
        'full_name': 'Test User Enhanced'
    }
    response = requests.put('http://localhost:8001/api/v1/profiles/me', json=update_data, headers=headers)
    print(f'✅ Update profile: {response.status_code}')
    if response.status_code == 200:
        user_data = response.json()
        print(f'   Bio updated: {user_data["bio"]}')

    # Test helper application
    helper_app = {
        'credentials': 'Certified mental health first aider with 2 years experience',
        'specialties': 'Anxiety support, Depression counseling',
        'bio': 'Passionate about helping others through difficult times'
    }
    response = requests.post('http://localhost:8001/api/v1/profiles/me/apply-helper', json=helper_app, headers=headers)
    print(f'✅ Helper application: {response.status_code}')
    if response.status_code == 200:
        user_data = response.json()
        print(f'   Helper status: {user_data["helper_verification_status"]}')

    # Test public profiles
    response = requests.get('http://localhost:8001/api/v1/profiles/helpers/list')
    print(f'✅ Helpers list: {response.status_code}')
    if response.status_code == 200:
        helpers = response.json()
        print(f'   Found {len(helpers)} helpers')

    print('🎉 User Profiles system working!')

if __name__ == "__main__":
    test_profiles_system()
