#!/usr/bin/env python3
"""
Debug Student Signup - Detailed Analysis
"""

import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5001"

def debug_signup():
    """Debug the signup process in detail"""
    print("🔍 Debugging Student Signup Process")
    print("=" * 50)
    
    test_student = {
        'first_name': 'Test',
        'last_name': 'Student',
        'email': f'debug{int(time.time())}@example.com',
        'phone': '+1234567890',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    session = requests.Session()
    
    try:
        # First get the signup page to check for any CSRF tokens or form requirements
        print("1️⃣ Getting signup page...")
        response = session.get(f"{BASE_URL}/auth/signup")
        print(f"   Status: {response.status_code}")
        
        # Check if there are any hidden form fields or CSRF tokens
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', {'action': '/auth/signup'})
        if form:
            print("   ✅ Signup form found")
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            if hidden_inputs:
                print(f"   Hidden inputs found: {len(hidden_inputs)}")
                for hidden in hidden_inputs:
                    test_student[hidden.get('name')] = hidden.get('value')
        else:
            print("   ❌ Signup form not found")
        
        # Try signup
        print(f"\n2️⃣ Attempting signup with data: {test_student}")
        response = session.post(f"{BASE_URL}/auth/signup", data=test_student, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"   Redirect to: {response.headers.get('Location')}")
            # Follow redirect
            redirect_response = session.get(response.headers.get('Location'))
            print(f"   Final status: {redirect_response.status_code}")
            if 'Welcome,' in redirect_response.text:
                print("   ✅ SUCCESS: Found welcome message in final page")
            else:
                print("   ⚠️  No welcome message found")
        else:
            # Check for errors in the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for flash messages
            flash_messages = soup.find_all(class_='flash-message') or soup.find_all(class_='alert')
            if flash_messages:
                print("   Flash messages found:")
                for msg in flash_messages:
                    print(f"     - {msg.get_text().strip()}")
            
            # Check for form errors
            error_divs = soup.find_all(class_='error') or soup.find_all(class_='field-error')
            if error_divs:
                print("   Form errors found:")
                for error in error_divs:
                    print(f"     - {error.get_text().strip()}")
            
            # Check page title for hints
            title = soup.find('title')
            if title:
                print(f"   Page title: {title.get_text()}")
        
        # Test if we can access protected route
        print(f"\n3️⃣ Testing access to protected route...")
        response = session.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   URL: {response.url}")
        if 'Welcome,' in response.text:
            print("   ✅ Can access chatbot with user greeting")
        elif '/welcome' in response.url:
            print("   ❌ Still redirected to welcome page")
        else:
            print("   ⚠️  Unexpected response")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_signup()
