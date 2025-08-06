#!/usr/bin/env python3
"""
Create Fresh Login Account for Testing Auto-Popup Chatbot Flow
This script creates a new student account without any existing user profile
so you can test the complete profile collection flow.
"""

import sys
import os
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

from datetime import datetime
import random
import string

def create_fresh_test_account():
    """Create a fresh test account for testing the auto-popup flow"""
    
    try:
        from app import app
        from human_handoff.models import db, Student, UserProfile
        
        with app.app_context():
            # Generate unique email with timestamp
            timestamp = datetime.now().strftime("%m%d_%H%M")
            test_email = f"test_user_{timestamp}@example.com"
            
            # Check if user already exists
            existing_user = Student.query.filter_by(email=test_email).first()
            if existing_user:
                print(f"❌ User with email {test_email} already exists")
                return None
            
            # Create new student account
            new_student = Student(
                first_name="Test",
                last_name="User",
                email=test_email,
                phone=None,  # No phone initially
                is_active=True
            )
            
            # Set a simple password
            password = "test123"
            new_student.set_password(password)
            
            # Add to database
            db.session.add(new_student)
            db.session.commit()
            
            # Verify no existing UserProfile (this is key for testing)
            existing_profile = UserProfile.query.filter_by(student_id=new_student.id).first()
            if existing_profile:
                print(f"⚠️  Found existing profile for student {new_student.id}, removing...")
                db.session.delete(existing_profile)
                db.session.commit()
                print("✅ Cleaned up existing profile")
            
            print("🎉 FRESH TEST ACCOUNT CREATED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📧 Email: {test_email}")
            print(f"🔑 Password: {password}")
            print(f"👤 Name: Test User")
            print(f"🆔 Student ID: {new_student.id}")
            print(f"📅 Created: {new_student.created_at}")
            print("=" * 60)
            
            print("\n🧪 TESTING INSTRUCTIONS:")
            print("1. Go to: http://127.0.0.1:5001/welcome")
            print("2. Click 'Already have an account? Login here'")
            print(f"3. Login with: {test_email} / {password}")
            print("4. Start chatting - you should see the auto-popup:")
            print("   'Hello! Welcome to EduConsult. Before we begin, may I have your full name please?'")
            print("5. Test the complete flow: Name → Phone → Continue")
            
            print("\n📱 TEST PHONE NUMBERS (Valid Nepali):")
            print("NTC: 9841234567, 9851234567, 9861234567")
            print("Ncell: 9801234567, 9811234567, 9821234567")
            
            return {
                'email': test_email,
                'password': password,
                'student_id': new_student.id,
                'name': 'Test User'
            }
            
    except Exception as e:
        print(f"❌ Error creating fresh test account: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_test_setup():
    """Verify the test setup is ready"""
    
    print("\n🔍 VERIFYING TEST ENVIRONMENT:")
    print("-" * 40)
    
    try:
        from app import app
        from human_handoff.models import db, Student, UserProfile
        
        with app.app_context():
            # Check database connection
            total_students = Student.query.count()
            total_profiles = UserProfile.query.count()
            
            print(f"✅ Database connected")
            print(f"✅ Total students in system: {total_students}")
            print(f"✅ Total user profiles: {total_profiles}")
            
            # Check phone validator
            try:
                from nepali_phone_validator import validate_nepali_phone
                test_result = validate_nepali_phone("9841234567")
                if test_result['valid'] and test_result['provider'] == 'NTC':
                    print("✅ Phone validator working")
                else:
                    print("❌ Phone validator issue")
            except Exception as e:
                print(f"❌ Phone validator error: {e}")
                
            print("✅ Test environment ready!")
            return True
            
    except Exception as e:
        print(f"❌ Environment verification failed: {e}")
        return False

def create_multiple_test_accounts():
    """Create multiple test accounts for comprehensive testing"""
    
    print("\n🔄 Creating Multiple Test Accounts...")
    accounts = []
    
    for i in range(3):
        account = create_fresh_test_account()
        if account:
            accounts.append(account)
            print(f"✅ Account {i+1} created")
        else:
            print(f"❌ Failed to create account {i+1}")
    
    if accounts:
        print(f"\n📋 CREATED {len(accounts)} TEST ACCOUNTS:")
        print("-" * 60)
        for i, acc in enumerate(accounts):
            print(f"{i+1}. {acc['email']} / {acc['password']}")
    
    return accounts

def main():
    """Main function"""
    
    print("🚀 FRESH TEST ACCOUNT CREATOR")
    print("=" * 60)
    print("Creating fresh login account for testing auto-popup chatbot flow")
    print("=" * 60)
    
    # Verify environment first
    if not verify_test_setup():
        print("❌ Environment verification failed. Please check server status.")
        return
    
    # Create fresh account
    account = create_fresh_test_account()
    
    if account:
        print("\n🎯 WHAT TO TEST:")
        print("-" * 40)
        print("✅ Auto-greeting message appears")
        print("✅ Name collection and validation")
        print("✅ Phone number collection and validation") 
        print("✅ Profile saved to database")
        print("✅ Normal chat continues after profile collection")
        print("✅ Subsequent logins skip profile collection")
        
        print("\n🌐 Quick Access Links:")
        print("• Login: http://127.0.0.1:5001/welcome")
        print("• Main Chat: http://127.0.0.1:5001")
        print("• User Management: http://127.0.0.1:5001/super-admin/user-management")
        
        # Ask if user wants multiple accounts
        try:
            response = input("\n❓ Create additional test accounts? (y/n): ").lower()
            if response == 'y':
                create_multiple_test_accounts()
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
    
    else:
        print("❌ Failed to create test account. Please check the error messages above.")

if __name__ == '__main__':
    main()
