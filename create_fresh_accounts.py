#!/usr/bin/env python3
"""
Script to create two fresh login accounts for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from human_handoff.models import db, Student
from datetime import datetime

def create_fresh_accounts():
    """Create two fresh login accounts"""
    
    with app.app_context():
        print("🔧 Creating Two Fresh Login Accounts")
        print("=" * 50)
        
        try:
            # Account 1
            print("\n📝 Creating Account 1...")
            account1 = Student(
                email='user1@example.com',
                username='user1',
                first_name='John',
                last_name='Doe',
                phone='9801111111',
                country_of_interest='United States',
                field_of_study='Computer Science',
                study_level='Bachelor',
                is_active=True,
                email_verified=True
            )
            account1.set_password('password123')
            
            db.session.add(account1)
            
            # Account 2
            print("📝 Creating Account 2...")
            account2 = Student(
                email='user2@example.com',
                username='user2',
                first_name='Jane',
                last_name='Smith',
                phone='9802222222',
                country_of_interest='Canada',
                field_of_study='Business Administration',
                study_level='Master',
                is_active=True,
                email_verified=True
            )
            account2.set_password('password123')
            
            db.session.add(account2)
            
            # Commit both accounts
            db.session.commit()
            
            print("✅ Successfully created two fresh accounts!")
            print(f"Account 1 ID: {account1.id}")
            print(f"Account 2 ID: {account2.id}")
            
            # Display login credentials
            print("\n🔑 LOGIN CREDENTIALS:")
            print("=" * 30)
            print("Account 1:")
            print(f"  Email: {account1.email}")
            print(f"  Username: {account1.username}")
            print(f"  Password: password123")
            print(f"  Name: {account1.get_full_name()}")
            print(f"  Interest: {account1.country_of_interest}")
            
            print("\nAccount 2:")
            print(f"  Email: {account2.email}")
            print(f"  Username: {account2.username}")
            print(f"  Password: password123")
            print(f"  Name: {account2.get_full_name()}")
            print(f"  Interest: {account2.country_of_interest}")
            
            print(f"\n🌐 You can now log in at: http://127.0.0.1:5001/auth/login")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating accounts: {e}")
            db.session.rollback()
            return False

def verify_accounts():
    """Verify the created accounts"""
    
    with app.app_context():
        print("\n🔍 VERIFYING CREATED ACCOUNTS:")
        print("=" * 35)
        
        try:
            # Get all students
            all_students = Student.query.all()
            print(f"Total students in database: {len(all_students)}")
            
            # Show the last two created accounts
            recent_accounts = Student.query.order_by(Student.created_at.desc()).limit(2).all()
            
            for i, student in enumerate(recent_accounts, 1):
                print(f"\nRecent Account {i}:")
                print(f"  ID: {student.id}")
                print(f"  Email: {student.email}")
                print(f"  Username: {student.username}")
                print(f"  Name: {student.get_full_name()}")
                print(f"  Phone: {student.phone}")
                print(f"  Created: {student.created_at}")
                print(f"  Active: {student.is_active}")
                print(f"  Email Verified: {student.email_verified}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying accounts: {e}")
            return False

def main():
    """Main function"""
    print("🚀 Fresh Account Creation Tool")
    print("Creating two new login accounts for testing...")
    
    # Create accounts
    success = create_fresh_accounts()
    
    if success:
        # Verify accounts
        verify_accounts()
        
        print("\n✅ ACCOUNT CREATION COMPLETE!")
        print("=" * 40)
        print("Two fresh accounts have been created and are ready for login.")
        print("Both accounts use password: password123")
        print("These accounts have no existing chat history or profiles.")
        
    else:
        print("\n❌ Account creation failed. Please check the error messages above.")

if __name__ == '__main__':
    main()
