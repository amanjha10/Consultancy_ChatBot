#!/usr/bin/env python3
"""
Create Fresh Test Account for Auto-Popup Chatbot Testing
This script creates a new student account with fresh credentials
"""

import sys
import os
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

from app import app
from human_handoff.models import db, Student
from datetime import datetime
import uuid

def create_fresh_test_account():
    """Create a fresh test account with new credentials"""
    
    print("🔧 CREATING FRESH TEST ACCOUNT")
    print("=" * 50)
    
    # Generate unique credentials
    timestamp = datetime.now().strftime("%m%d_%H%M")
    unique_id = str(uuid.uuid4())[:8]
    
    # Fresh credentials
    email = f"testuser_{timestamp}@example.com"
    password = "testpass123"
    first_name = "Test"
    last_name = f"User{timestamp}"
    
    try:
        with app.app_context():
            # Check if email already exists
            existing_student = Student.query.filter_by(email=email).first()
            if existing_student:
                print(f"⚠️  Email {email} already exists, generating new one...")
                email = f"testuser_{unique_id}@example.com"
            
            # Create new student
            student = Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=None  # Will be collected during auto-popup flow
            )
            student.set_password(password)
            
            db.session.add(student)
            db.session.commit()
            
            print("✅ SUCCESS! Fresh test account created:")
            print("-" * 50)
            print(f"📧 Email: {email}")
            print(f"🔒 Password: {password}")
            print(f"👤 Name: {first_name} {last_name}")
            print(f"🆔 Student ID: {student.id}")
            print("-" * 50)
            
            print("\n📋 TESTING INSTRUCTIONS:")
            print("1. Go to: http://127.0.0.1:5001")
            print("2. You'll be redirected to signup/login page")
            print("3. Click 'Login' tab")
            print("4. Use the credentials above to login")
            print("5. Start chatting - you'll see the auto-popup profile collection!")
            
            print("\n🎯 EXPECTED AUTO-POPUP FLOW:")
            print("1. Bot: 'Hello! Welcome to EduConsult. Before we begin, may I have your full name please?'")
            print("2. You: Enter your name")
            print("3. Bot: 'Nice to meet you, [Name]! Now, could you please provide your phone number for verification?'")
            print("4. You: Enter Nepali phone number (e.g., 9841234567)")
            print("5. Bot: '✅ Thank you! Your [NTC/Ncell] number has been verified. Now, how can I help you with your study abroad plans?'")
            
            return {
                'email': email,
                'password': password,
                'name': f"{first_name} {last_name}",
                'student_id': student.id
            }
            
    except Exception as e:
        print(f"❌ Error creating test account: {e}")
        return None

if __name__ == '__main__':
    account = create_fresh_test_account()
    if account:
        print(f"\n🎉 Account ready for testing the auto-popup chatbot flow!")
    else:
        print(f"\n❌ Failed to create test account. Please check the error above.")
