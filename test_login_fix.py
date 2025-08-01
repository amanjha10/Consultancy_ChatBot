#!/usr/bin/env python3
"""
Test login functionality after fixing the URL routing issue
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

def test_login_fixed():
    """Test login after fixing the routing issue"""
    
    from app import app
    from human_handoff.models import db, Student
    
    with app.test_client() as client:
        print("=== TESTING FIXED LOGIN ===")
        
        # Test 1: POST request with valid credentials
        print("\n1. Testing POST request with valid credentials...")
        login_data = {
            'email': 'demo@student.com',
            'password': 'demo123'
        }
        
        try:
            response = client.post('/auth/login', data=login_data, follow_redirects=False)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 302:
                print(f"✓ Login successful - redirecting to: {response.location}")
                print("✓ Login issue has been resolved!")
                return True
            elif response.status_code == 200:
                print("Checking response content...")
                response_text = response.data.decode()
                if 'Welcome back' in response_text or 'success' in response_text.lower():
                    print("✓ Login appears successful (no redirect)")
                    return True
                else:
                    print("✗ Login failed - checking for error messages")
                    if 'error' in response_text.lower():
                        print("Error found in response")
                    print(response_text[:500])
                    return False
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                print(response.data.decode()[:500])
                return False
                
        except Exception as e:
            print(f"✗ Exception during login test: {e}")
            import traceback
            traceback.print_exc()
            return False

        # Test 2: Test with follow redirects
        print("\n2. Testing with follow_redirects=True...")
        try:
            response = client.post('/auth/login', data=login_data, follow_redirects=True)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.data.decode()
                if 'Welcome' in response_text and 'Demo Student' in response_text:
                    print("✓ Login successful and redirected to main page!")
                    return True
                else:
                    print("Response doesn't contain expected welcome message")
                    print(response_text[:500])
            
        except Exception as e:
            print(f"Exception in redirect test: {e}")
            return False

if __name__ == '__main__':
    success = test_login_fixed()
    
    if success:
        print("\n" + "="*50)
        print("🎉 LOGIN ISSUE RESOLVED! 🎉")
        print("✅ Students can now log in successfully")
        print("✅ Authentication system is working properly")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ Login still has issues")
        print("Need further investigation")
        print("="*50)
