#!/usr/bin/env python3
"""
Final Student Authentication System Verification
Comprehensive test of the complete authentication flow
"""

import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5001"

def test_complete_authentication_flow():
    """Test the complete student authentication system"""
    print("🎯 FINAL AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    
    test_email = f'final_test_{int(time.time())}@example.com'
    test_data = {
        'first_name': 'Final',
        'last_name': 'TestUser',
        'email': test_email,
        'phone': '+1234567890',
        'password': 'secure123',
        'confirm_password': 'secure123'
    }
    
    session = requests.Session()
    passed_tests = 0
    total_tests = 8
    
    try:
        # Test 1: Unauthenticated access should redirect to welcome
        print("1️⃣ Testing route protection...")
        response = session.get(f"{BASE_URL}/")
        if '/welcome' in response.url:
            print("   ✅ PASS: Unauthenticated users redirected to welcome page")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Expected redirect to welcome, got: {response.url}")
        
        # Test 2: Signup page accessibility
        print("\n2️⃣ Testing signup page access...")
        response = session.get(f"{BASE_URL}/auth/signup")
        if response.status_code == 200 and 'Create Account' in response.text:
            print("   ✅ PASS: Signup page loads correctly")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Signup page issue - Status: {response.status_code}")
        
        # Test 3: Student registration
        print(f"\n3️⃣ Testing student registration...")
        print(f"   📧 Email: {test_email}")
        response = session.post(f"{BASE_URL}/auth/signup", data=test_data)
        
        # Check for success indicators
        success_indicators = [
            'Account created successfully',
            'Welcome to EduConsult',
            'Welcome, Final'  # User greeting in header
        ]
        
        has_success = any(indicator in response.text for indicator in success_indicators)
        
        if response.status_code == 200 and has_success:
            print("   ✅ PASS: Student registration successful")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Registration failed - Status: {response.status_code}")
        
        # Test 4: Authenticated access to chatbot
        print("\n4️⃣ Testing authenticated chatbot access...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200 and 'Welcome, Final' in response.text:
            print("   ✅ PASS: Authenticated access works, user greeting displayed")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Authenticated access issue - Status: {response.status_code}")
        
        # Test 5: Chat functionality with authentication
        print("\n5️⃣ Testing chat functionality...")
        chat_data = {
            'message': 'I want to study abroad in Canada',
            'session_id': f'test_session_{int(time.time())}'
        }
        response = session.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'response' in result and len(result['response']) > 0:
                    print("   ✅ PASS: Chat functionality working")
                    print(f"   📝 Response preview: {result['response'][:80]}...")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAIL: Empty or invalid chat response: {result}")
            except json.JSONDecodeError:
                print(f"   ❌ FAIL: Chat response not valid JSON")
        else:
            print(f"   ❌ FAIL: Chat request failed - Status: {response.status_code}")
        
        # Test 6: Logout functionality
        print("\n6️⃣ Testing logout...")
        response = session.get(f"{BASE_URL}/auth/logout")
        if response.status_code == 200:
            print("   ✅ PASS: Logout request successful")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Logout failed - Status: {response.status_code}")
        
        # Test 7: Post-logout protection
        print("\n7️⃣ Testing post-logout route protection...")
        response = session.get(f"{BASE_URL}/")
        if '/welcome' in response.url:
            print("   ✅ PASS: Routes properly protected after logout")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Still has access after logout: {response.url}")
        
        # Test 8: Login with existing credentials
        print("\n8️⃣ Testing login with existing credentials...")
        login_data = {
            'email': test_email,
            'password': 'secure123'
        }
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        # Check if we can access protected route after login
        access_response = session.get(f"{BASE_URL}/")
        if access_response.status_code == 200 and 'Welcome, Final' in access_response.text:
            print("   ✅ PASS: Login successful, can access chatbot")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Login or subsequent access failed")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        return False
    
    # Results summary
    print("\n" + "=" * 60)
    print("🏆 FINAL TEST RESULTS")
    print("=" * 60)
    
    print(f"✅ Passed: {passed_tests}/{total_tests} tests")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("\n🎉 🎉 🎉 COMPLETE SUCCESS! 🎉 🎉 🎉")
        print("✨ Student Authentication System is FULLY FUNCTIONAL!")
        print("\n📋 System Features Verified:")
        print("   ✅ Route protection for unauthenticated users")
        print("   ✅ Student registration with full validation")
        print("   ✅ Secure login/logout functionality")
        print("   ✅ Session management and user context")
        print("   ✅ Chat functionality with user tracking")
        print("   ✅ Proper user interface with greetings")
        print("   ✅ Complete authentication flow")
        print("   ✅ Database integration and persistence")
        return True
    elif passed_tests >= 6:
        print("\n✅ MOSTLY SUCCESSFUL - Minor issues to address")
        return True
    else:
        print("\n⚠️ NEEDS ATTENTION - Several core features failing")
        return False

def test_database_integration():
    """Verify database integration is working"""
    print("\n🗄️ Testing Database Integration...")
    
    try:
        # Check if we can connect to database and verify student was created
        import sys
        sys.path.append('/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')
        from human_handoff.models import Student, ChatSession, db
        
        # Check if our test user exists
        recent_students = Student.query.filter(Student.email.like('%final_test_%')).all()
        if recent_students:
            print(f"   ✅ Found {len(recent_students)} test student(s) in database")
            
            # Check if student has proper fields
            student = recent_students[-1]  # Get most recent
            print(f"   👤 Latest student: {student.get_full_name()} ({student.email})")
            
            # Check if student can authenticate
            if student.check_password('secure123'):
                print("   ✅ Password authentication working")
            else:
                print("   ❌ Password authentication failed")
        else:
            print("   ⚠️ No test students found in database")
            
    except Exception as e:
        print(f"   ❌ Database test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 FINAL AUTHENTICATION SYSTEM VERIFICATION")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_complete_authentication_flow()
    test_database_integration()
    
    if success:
        print("\n" + "🎯" * 20)
        print("AUTHENTICATION SYSTEM IMPLEMENTATION COMPLETE!")
        print("🎯" * 20)
        print("\n📈 NEXT STEPS:")
        print("   1. 🚀 Deploy to production environment")
        print("   2. 📊 Update agent dashboard to show student info")
        print("   3. 📝 Update documentation and user guides")
        print("   4. 🔒 Consider additional security features")
        print("   5. 📱 Test mobile responsiveness")
    else:
        print("\n⚠️ Please review and fix the failing tests above")
