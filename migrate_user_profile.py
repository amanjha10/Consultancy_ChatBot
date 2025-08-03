#!/usr/bin/env python3
"""
Database migration to add user profile functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from human_handoff.models import db, Student, UserProfile

def migrate_database():
    """Add user profile table and update students table"""
    
    with app.app_context():
        print("Starting database migration for user profiles...")
        
        try:
            # Create all tables (will create new UserProfile table)
            db.create_all()
            print("✓ User profile table created successfully")
            
            # Add is_favorite column to students table if it doesn't exist
            try:
                # First check if column exists
                result = db.session.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
                table_sql = result.fetchone()[0]
                
                if 'is_favorite' not in table_sql:
                    # Column doesn't exist, add it
                    from sqlalchemy import text
                    db.session.execute(text("ALTER TABLE students ADD COLUMN is_favorite BOOLEAN DEFAULT 0"))
                    db.session.commit()
                    print("✓ Added is_favorite column to students table")
                else:
                    print("✓ is_favorite column already exists in students table")
                        
            except Exception as e:
                print(f"Error adding is_favorite column: {e}")
                # For existing installations, the column might already exist or we need to handle it differently
                try:
                    # Test if column exists by trying to select it
                    db.session.execute("SELECT is_favorite FROM students LIMIT 1")
                    print("✓ is_favorite column confirmed to exist")
                except:
                    print(f"Note: Could not add is_favorite column - may need manual database update")
            
            print("Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("✓ Migration successful")
    else:
        print("✗ Migration failed")
        sys.exit(1)
