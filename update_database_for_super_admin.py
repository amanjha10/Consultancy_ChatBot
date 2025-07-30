#!/usr/bin/env python3
"""
Update database schema to support super admin functionality
"""

from human_handoff.models import db, SuperAdmin, AgentSession
from app import app

def update_database():
    """Update database schema for super admin support"""
    print('🔄 Updating database schema for super admin support...')
    
    with app.app_context():
        try:
            # Create all tables (this will create new tables and add new columns)
            db.create_all()
            
            # Create default super admin if it doesn't exist
            super_admin = SuperAdmin.query.filter_by(admin_id='super_admin').first()
            if not super_admin:
                super_admin = SuperAdmin(
                    admin_id='super_admin',
                    name='Super Administrator',
                    email='admin@educonsult.com',
                    password_hash='hashed_password',  # In production, hash this properly
                    is_active=True
                )
                db.session.add(super_admin)
                db.session.commit()
                print('✅ Created default super admin account')
            else:
                print('✅ Super admin account already exists')
            
            print('✅ Database schema updated successfully!')
            print('\n📋 Super Admin Login Credentials:')
            print('   Admin ID: super_admin')
            print('   Password: admin123')
            print('   URL: http://localhost:5000/super-admin/login')
            
            return True
            
        except Exception as e:
            print(f'❌ Error updating database: {e}')
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = update_database()
    if success:
        print('\n🎉 Super admin system ready!')
    else:
        print('\n💥 Failed to update database!')
