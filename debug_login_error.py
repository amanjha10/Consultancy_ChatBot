#!/usr/bin/env python3
"""
Debug script to identify the specific login error
"""

import sys
import os
import traceback
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

# Set up Flask app context
from app import app
from human_handoff.models import db, Student
from flask_login import login_user
from flask import session

def debug_login_process():
    """Debug the login process step by step"""
    
    with app.app_context():
        print("=== DEBUGGING LOGIN PROCESS ===")
        
        # Test 1: Check if student exists
        print("\n1. Checking if demo student exists...")
        student = Student.query.filter_by(email='demo@student.com').first()
        if student:
            print(f"✓ Student found: {student.get_full_name()} (ID: {student.id})")
            print(f"  - Email: {student.email}")
            print(f"  - Active: {student.is_active}")
            print(f"  - Created: {student.created_at}")
            print(f"  - Last login: {student.last_login}")
        else:
            print("✗ Student not found!")
            return False
        
        # Test 2: Check password verification
        print("\n2. Testing password verification...")
        try:
            password_valid = student.check_password('demo123')
            print(f"✓ Password check result: {password_valid}")
        except Exception as e:
            print(f"✗ Password check failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 3: Test database update (last_login)
        print("\n3. Testing database update...")
        try:
            original_last_login = student.last_login
            student.last_login = datetime.utcnow()
            db.session.commit()
            print(f"✓ Database update successful")
            print(f"  - Original last_login: {original_last_login}")
            print(f"  - New last_login: {student.last_login}")
        except Exception as e:
            print(f"✗ Database update failed: {e}")
            traceback.print_exc()
            db.session.rollback()
            return False
        
        # Test 4: Test Flask-Login login_user
        print("\n4. Testing Flask-Login login_user()...")
        try:
            with app.test_request_context('/login', method='POST'):
                result = login_user(student, remember=False)
                print(f"✓ login_user() result: {result}")
        except Exception as e:
            print(f"✗ login_user() failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 5: Test session operations
        print("\n5. Testing session operations...")
        try:
            with app.test_request_context('/login', method='POST') as ctx:
                ctx.session['student_id'] = student.id
                ctx.session['student_name'] = student.get_full_name()
                ctx.session['student_email'] = student.email
                print(f"✓ Session operations successful")
                print(f"  - student_id: {ctx.session['student_id']}")
                print(f"  - student_name: {ctx.session['student_name']}")
                print(f"  - student_email: {ctx.session['student_email']}")
        except Exception as e:
            print(f"✗ Session operations failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        return True

def test_complete_login_flow():
    """Test the complete login flow with exception handling"""
    
    with app.app_context():
        print("\n=== TESTING COMPLETE LOGIN FLOW ===")
        
        try:
            # Simulate the login route logic
            email = 'demo@student.com'
            password = 'demo123'
            remember_me = False
            
            print(f"Attempting login for: {email}")
            
            # Check credentials
            student = Student.query.filter_by(email=email).first()
            if not student or not student.check_password(password):
                print("✗ Invalid credentials")
                return False
            
            if not student.is_active:
                print("✗ Account inactive")
                return False
            
            print("✓ Credentials validated")
            
            # Create a test request context
            with app.test_request_context('/login', method='POST') as ctx:
                # Update last login
                student.last_login = datetime.utcnow()
                db.session.commit()
                print("✓ Last login updated")
                
                # Log in the user
                login_result = login_user(student, remember=remember_me)
                print(f"✓ login_user() result: {login_result}")
                
                # Store user info in session
                ctx.session['student_id'] = student.id
                ctx.session['student_name'] = student.get_full_name()
                ctx.session['student_email'] = student.email
                print("✓ Session data stored")
                
                print("✓ COMPLETE LOGIN FLOW SUCCESSFUL")
                return True
                
        except Exception as e:
            print(f"✗ LOGIN FLOW FAILED: {e}")
            print(f"Exception type: {type(e).__name__}")
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Starting login debug process...")
    
    # Test individual components
    debug_login_process()
    
    # Test complete flow
    test_complete_login_flow()
    
    print("\nDebug complete!")
