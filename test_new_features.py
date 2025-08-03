#!/usr/bin/env python3
"""
Test script for new user profile collection and user management features
"""

import sys
import os
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

from app import app
from human_handoff.models import db, UserProfile, Student
from nepali_phone_validator import validate_nepali_phone, format_nepali_phone

def test_phone_validation():
    """Test Nepali phone number validation"""
    print("=== Testing Phone Number Validation ===")
    
    test_cases = [
        ('9801234567', True, 'Ncell'),
        ('9841234567', True, 'NTC'),
        ('9621234567', True, 'Smart Cell'),
        ('9771234567', False, 'Invalid prefix'),
        ('98012345', False, 'Too short'),
        ('98012345678', False, 'Too long'),
        ('980-123-4567', True, 'Ncell with formatting'),
        ('abc1234567', False, 'Invalid characters'),
    ]
    
    for phone, expected_valid, description in test_cases:
        result = validate_nepali_phone(phone)
        status = "✓" if result['valid'] == expected_valid else "✗"
        print(f"{status} {phone:15} → {result['message']}")
        if result['valid']:
            print(f"    Provider: {result['provider']}, Formatted: {format_nepali_phone(phone)}")
    
    print()

def test_user_profile_creation():
    """Test user profile creation"""
    print("=== Testing User Profile Creation ===")
    
    with app.app_context():
        try:
            # Create a test student
            test_student = Student(
                email='test_profile@example.com',
                first_name='Test',
                last_name='User',
                is_active=True
            )
            test_student.set_password('testpass123')
            
            db.session.add(test_student)
            db.session.commit()
            
            # Create a test user profile
            test_profile = UserProfile(
                student_id=test_student.id,
                session_id='test_session_123',
                name='Test User Profile',
                phone='9801234567'
            )
            
            db.session.add(test_profile)
            db.session.commit()
            
            print(f"✓ Created test user profile: {test_profile.name}")
            print(f"  Phone: {test_profile.phone}")
            print(f"  Session: {test_profile.session_id}")
            print(f"  Student ID: {test_profile.student_id}")
            
            # Test retrieval
            retrieved = UserProfile.query.filter_by(session_id='test_session_123').first()
            if retrieved:
                print(f"✓ Successfully retrieved profile: {retrieved.to_dict()}")
            else:
                print("✗ Failed to retrieve profile")
                
        except Exception as e:
            print(f"✗ Error creating user profile: {e}")
            db.session.rollback()
    
    print()

def test_database_structure():
    """Test database structure"""
    print("=== Testing Database Structure ===")
    
    with app.app_context():
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Check tables
            tables = inspector.get_table_names()
            required_tables = ['students', 'user_profiles', 'chat_sessions', 'messages']
            
            for table in required_tables:
                if table in tables:
                    print(f"✓ Table '{table}' exists")
                    
                    # Show columns for user_profiles table
                    if table == 'user_profiles':
                        columns = inspector.get_columns(table)
                        print(f"  Columns: {', '.join([col['name'] for col in columns])}")
                else:
                    print(f"✗ Table '{table}' missing")
            
            # Check students table for is_favorite column
            students_columns = inspector.get_columns('students')
            student_column_names = [col['name'] for col in students_columns]
            
            if 'is_favorite' in student_column_names:
                print("✓ 'is_favorite' column exists in students table")
            else:
                print("✗ 'is_favorite' column missing from students table")
                
        except Exception as e:
            print(f"✗ Error checking database structure: {e}")
    
    print()

def test_user_management_functionality():
    """Test user management features"""
    print("=== Testing User Management Functionality ===")
    
    with app.app_context():
        try:
            # Get all user profiles
            profiles = UserProfile.query.all()
            print(f"✓ Found {len(profiles)} user profiles")
            
            # Test favorite functionality
            if profiles:
                test_profile = profiles[0]
                original_favorite = test_profile.is_favorite
                
                # Toggle favorite
                test_profile.is_favorite = not original_favorite
                db.session.commit()
                
                # Check if change persisted
                updated_profile = UserProfile.query.get(test_profile.id)
                if updated_profile.is_favorite != original_favorite:
                    print("✓ Favorite toggle functionality works")
                else:
                    print("✗ Favorite toggle failed")
                
                # Restore original state
                test_profile.is_favorite = original_favorite
                db.session.commit()
            
            # Test profile with student join
            profile_with_student = db.session.query(UserProfile, Student).join(
                Student, UserProfile.student_id == Student.id
            ).first()
            
            if profile_with_student:
                profile, student = profile_with_student
                print(f"✓ Join query works: {profile.name} ({student.email})")
            else:
                print("✓ No profiles with students found (this is ok for empty database)")
                
        except Exception as e:
            print(f"✗ Error testing user management: {e}")
    
    print()

def main():
    """Run all tests"""
    print("Running comprehensive test suite for new features...\n")
    
    test_phone_validation()
    test_database_structure()
    test_user_profile_creation()
    test_user_management_functionality()
    
    print("Test suite completed!")

if __name__ == '__main__':
    main()
