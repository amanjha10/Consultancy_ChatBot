#!/usr/bin/env python3
"""
Test script to verify name and phone collection behavior
"""

import sys
import os
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

from app import app
from human_handoff.models import db, UserProfile, Student

def test_profile_collection_logic():
    """Test if profile collection works correctly"""
    print("=== Testing Profile Collection Logic ===")
    
    with app.app_context():
        try:
            # Check current state
            profiles = UserProfile.query.all()
            students = Student.query.all()
            
            print(f"Current database state:")
            print(f"  Total Students: {len(students)}")
            print(f"  Total UserProfiles: {len(profiles)}")
            
            # Test for each student
            for student in students:
                student_profiles = UserProfile.query.filter_by(student_id=student.id).all()
                print(f"\nStudent: {student.email} (ID: {student.id})")
                print(f"  Has {len(student_profiles)} profile(s)")
                
                if student_profiles:
                    print(f"  Latest profile: {student_profiles[-1].name} - {student_profiles[-1].phone}")
                    print(f"  → Should NOT ask for name/phone again")
                else:
                    print(f"  → SHOULD ask for name/phone")
                    
        except Exception as e:
            print(f"Error: {e}")

def create_fresh_student_for_testing():
    """Create a new student without any profile for testing"""
    print("\n=== Creating Fresh Student for Testing ===")
    
    with app.app_context():
        try:
            # Create a new student
            new_student = Student(
                email='fresh_test@example.com',
                first_name='Fresh',
                last_name='TestUser',
                is_active=True
            )
            new_student.set_password('testpass123')
            
            db.session.add(new_student)
            db.session.commit()
            
            print(f"✅ Created fresh student: {new_student.email} (ID: {new_student.id})")
            print(f"   This student should be asked for name and phone")
            
            return new_student.id
            
        except Exception as e:
            print(f"Error creating fresh student: {e}")
            return None

if __name__ == '__main__':
    test_profile_collection_logic()
    fresh_student_id = create_fresh_student_for_testing()
    
    print(f"\n=== Summary ===")
    print(f"Students with profiles should NOT be asked for name/phone")
    print(f"Students without profiles (like student ID {fresh_student_id}) SHOULD be asked")
    print(f"\nTo test: Log in as fresh_test@example.com and start a chat")
