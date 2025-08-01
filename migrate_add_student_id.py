#!/usr/bin/env python3
"""
Migration script to add student_id column to chat_sessions table
"""

import sqlite3
import os
from flask import Flask
from app import app, db
from human_handoff.models import ChatSession

def add_student_id_column():
    """Add student_id column to existing chat_sessions table"""
    
    # Use the actual database path found in the instance folder
    db_path = "/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot/instance/human_handoff.db"
    
    print(f"📁 Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if student_id column already exists
        cursor.execute("PRAGMA table_info(chat_sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'student_id' in columns:
            print("✅ student_id column already exists")
            conn.close()
            return True
        
        print("🔧 Adding student_id column to chat_sessions table...")
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE chat_sessions 
            ADD COLUMN student_id INTEGER
        """)
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_student_id 
            ON chat_sessions(student_id)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added student_id column")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        with app.app_context():
            # Test that we can query the table with new column
            sessions = ChatSession.query.all()
            print(f"✅ Migration verified - can access {len(sessions)} chat sessions")
            
            # Show table structure
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(chat_sessions)"))
            columns = result.fetchall()
            
            print("\n📋 Current chat_sessions table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
            return True
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    success = add_student_id_column()
    
    if success:
        print("\n🔍 Verifying migration...")
        verify_migration()
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
