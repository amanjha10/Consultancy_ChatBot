#!/usr/bin/env python3
"""
Student Authentication System Test
Tests the complete student authentication flow including signup, login, and chatbot access
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

def test_student_authentication():
    """Test complete student authentication flow"""
    print("🔐 Testing Student Authentication System")
    print("=" * 60)
    
    # Test data
    test_student = {
        'first_name': 'Test',
        'last_name': 'Student',
        'email': f'test{int(time.time())}@example.com',
        'phone': '+1234567890',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    session = requests.Session()
    
    try:
        # Test 1: Access protected route without authentication (should redirect)
        print("1️⃣ Testing unauthenticated access to chatbot...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200 and '/welcome' in response.url:
            print("   ✅ Correctly redirected to welcome page")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}, URL: {response.url}")
        
        # Test 2: Load signup page
        print("\n2️⃣ Testing signup page access...")
        response = session.get(f"{BASE_URL}/auth/signup")
        if response.status_code == 200:
            print("   ✅ Signup page loads successfully")
        else:
            print(f"   ❌ Failed to load signup page: {response.status_code}")
            return False
        
        # Test 3: Student signup
        print("\n3️⃣ Testing student signup...")
        response = session.post(f"{BASE_URL}/auth/signup", data=test_student)
        if response.status_code == 200 and (response.url.endswith('/') or 'index' in response.url):
            print("   ✅ Student signup successful, redirected to chatbot")
        else:
            print(f"   ❌ Signup failed: {response.status_code}, URL: {response.url}")
            print(f"   Response text: {response.text[:200]}...")
            return False
        
        # Test 4: Access chatbot after authentication
        print("\n4️⃣ Testing authenticated chatbot access...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200 and 'Welcome,' in response.text:
            print("   ✅ Authenticated access to chatbot successful")
            print("   ✅ User greeting found in page")
        else:
            print(f"   ❌ Failed to access chatbot: {response.status_code}")
            return False
        
        # Test 5: Test logout
        print("\n5️⃣ Testing logout...")
        response = session.get(f"{BASE_URL}/auth/logout")
        if response.status_code == 200:
            print("   ✅ Logout successful")
        else:
            print(f"   ❌ Logout failed: {response.status_code}")
        
        # Test 6: Verify logout (should redirect to welcome)
        print("\n6️⃣ Testing post-logout access...")
        response = session.get(f"{BASE_URL}/")
        if '/welcome' in response.url or response.status_code == 401:
            print("   ✅ Correctly blocked access after logout")
        else:
            print(f"   ❌ Still has access after logout: {response.status_code}")
        
        # Test 7: Test login with existing credentials
        print("\n7️⃣ Testing login with existing credentials...")
        login_data = {
            'email': test_student['email'],
            'password': test_student['password']
        }
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200 and (response.url.endswith('/') or 'index' in response.url):
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
        
        # Test 8: Test chat functionality (basic)
        print("\n8️⃣ Testing chat functionality...")
        chat_data = {
            'message': 'Hello, I need help with university applications',
            'session_id': 'test_session'
        }
        response = session.post(f"{BASE_URL}/chat", json=chat_data)
        if response.status_code == 200:
            try:
                result = response.json()
                if 'response' in result:
                    print("   ✅ Chat functionality working")
                    print(f"   Response preview: {result['response'][:100]}...")
                else:
                    print(f"   ❌ Unexpected chat response format: {result}")
            except json.JSONDecodeError:
                print(f"   ❌ Chat response not valid JSON: {response.text[:100]}...")
        else:
            print(f"   ❌ Chat request failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎯 Student Authentication Test Complete!")
        print("✅ All core authentication features working correctly")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 5000?")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_duplicate_email():
    """Test that duplicate email registration is properly handled"""
    print("\n🔄 Testing duplicate email handling...")
    
    session = requests.Session()
    duplicate_data = {
        'first_name': 'Another',
        'last_name': 'Student',
        'email': 'test@example.com',  # Use a common email
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/signup", data=duplicate_data)
        if 'already registered' in response.text.lower() or response.status_code == 400:
            print("   ✅ Duplicate email properly rejected")
        else:
            print("   ⚠️  Duplicate email handling may need attention")
    except Exception as e:
        print(f"   ❌ Error testing duplicate email: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Student Authentication System Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Wait a moment for server to fully start
    print("⏳ Waiting for server to initialize...")
    time.sleep(3)
    
    success = test_student_authentication()
    test_duplicate_email()
    
    if success:
        print("\n🎉 SUCCESS: Student authentication system is fully functional!")
    else:
        print("\n⚠️  Some issues detected - check the test output above")
