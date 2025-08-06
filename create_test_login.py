#!/usr/bin/env python3
"""
Create a fresh test login account for testing the auto-popup chatbot flow
"""

import sys
import os
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

from datetime import datetime
import hashlib

def create_fresh_test_login():
    """Create a fresh test login account"""
    print("🔑 Creating Fresh Test Login Account")
    print("=" * 50)
    
    try:
        from app import app
        from human_handoff.models import db, Student
        
        with app.app_context():
            # Generate unique credentials with timestamp
            timestamp = datetime.now().strftime("%m%d_%H%M")
            email = f"test_user_{timestamp}@example.com"
            password = "test123"
            name = f"Test User {timestamp}"
            
            # Check if user already exists
            existing_user = Student.query.filter_by(email=email).first()
            if existing_user:
                print(f"❌ User with email {email} already exists")
                return None
            
            # Create new student account
            new_student = Student(
                name=name,
                email=email,
                phone="9841234567",  # Valid Nepali number for testing
                password=hashlib.sha256(password.encode()).hexdigest(),
                is_active=True
            )
            
            db.session.add(new_student)
            db.session.commit()
            
            print("✅ Fresh test login account created successfully!")
            print("-" * 50)
            print(f"📧 Email: {email}")
            print(f"🔒 Password: {password}")
            print(f"👤 Name: {name}")
            print(f"📱 Phone: 9841234567")
            print("-" * 50)
            print("🌐 Login URL: http://127.0.0.1:5001/welcome")
            print("🤖 Test chatbot: http://127.0.0.1:5001")
            print("-" * 50)
            print("📝 Testing Instructions:")
            print("1. Go to http://127.0.0.1:5001/welcome")
            print("2. Login with the credentials above")
            print("3. After login, you'll be redirected to the chatbot")
            print("4. The chatbot should auto-popup with greeting message")
            print("5. Test the profile collection flow")
            
            return {
                'email': email,
                'password': password,
                'name': name,
                'phone': '9841234567'
            }
            
    except Exception as e:
        print(f"❌ Error creating test login: {e}")
        return None

def verify_server_running():
    """Check if the server is running"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:5001/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on port 5001")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not running. Please start it first:")
        print("   cd /Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot")
        print("   python app.py")
        return False

if __name__ == '__main__':
    print("🚀 FRESH TEST LOGIN CREATOR")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Check if server is running
    if verify_server_running():
        credentials = create_fresh_test_login()
        
        if credentials:
            print("\n🎉 SUCCESS! Your fresh test login is ready.")
            print("\n🔄 NEXT STEPS:")
            print("1. Open browser and go to: http://127.0.0.1:5001/welcome")
            print(f"2. Login with: {credentials['email']} / {credentials['password']}")
            print("3. Test the auto-popup chatbot flow")
            print("4. Verify profile collection and phone validation")
            print("5. Check user management dashboard")
        else:
            print("\n❌ Failed to create test login. Check the error above.")
    else:
        print("\n⚠️  Please start the server first, then run this script again.")
