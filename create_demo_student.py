#!/usr/bin/env python3
"""
Create a test student account with known credentials
"""

from human_handoff.models import Student, db
from app import app

def create_test_student():
    """Create a test student with known credentials"""
    
    with app.app_context():
        # Check if test user already exists
        test_email = "demo@student.com"
        existing_student = Student.query.filter_by(email=test_email).first()
        
        if existing_student:
            print(f"✅ Test student already exists!")
            print(f"📧 Email: {test_email}")
            print(f"🔑 Password: demo123")
            print(f"👤 Name: {existing_student.get_full_name()}")
            return
        
        # Create new test student
        try:
            student = Student(
                first_name="Demo",
                last_name="Student", 
                email=test_email,
                phone="+1234567890"
            )
            student.set_password("demo123")
            
            db.session.add(student)
            db.session.commit()
            
            print("🎉 Test student created successfully!")
            print(f"📧 Email: {test_email}")
            print(f"🔑 Password: demo123")
            print(f"👤 Name: {student.get_full_name()}")
            print()
            print("💡 You can now login with these credentials!")
            
        except Exception as e:
            print(f"❌ Error creating test student: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_test_student()
