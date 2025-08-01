#!/usr/bin/env python3
"""
Migrate existing agents to include password authentication
"""

import sqlite3
import os
from human_handoff.models import db, Agent
from app import app

def migrate_agent_passwords():
    """Add password hashes to existing agents"""
    print('🔄 Migrating agent authentication...')
    
    with app.app_context():
        try:
            # First, check if the password_hash column exists
            db_path = os.path.join(app.instance_path, 'human_handoff.db')
            
            # Use raw SQL to add the column if it doesn't exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if password_hash column exists
            cursor.execute("PRAGMA table_info(agents)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'password_hash' not in columns:
                print('   📋 Adding password_hash column to agents table...')
                cursor.execute('ALTER TABLE agents ADD COLUMN password_hash TEXT')
                conn.commit()
                print('   ✅ Added password_hash column')
                
            if 'password_set' not in columns:
                print('   📋 Adding password_set column to agents table...')
                cursor.execute('ALTER TABLE agents ADD COLUMN password_set BOOLEAN DEFAULT 0')
                conn.commit()
                print('   ✅ Added password_set column')
            
            conn.close()
            
            # Now create all tables (this will handle any other schema changes)
            db.create_all()
            
            # Import werkzeug here to generate password hashes
            from werkzeug.security import generate_password_hash
            
            # Get all agents and reset their passwords for the new system
            agents = Agent.query.all()
            
            updated_count = 0
            for agent in agents:
                # Reset all agents to require first-time password setup
                agent.password_hash = None
                agent.password_set = False
                updated_count += 1
                print(f'   ✅ Reset password for {agent.name} ({agent.agent_id}) - First login required')
            
            if updated_count > 0:
                db.session.commit()
                print(f'✅ Successfully reset {updated_count} agents for first-time password setup')
                print('🔑 All agents must set their own password on first login')
            else:
                print('✅ No agents found to update')
            
            # Display current agent login information
            print('\n📋 Agent Login Credentials:')
            all_agents = Agent.query.filter_by(is_active=True).all()
            for agent in all_agents:
                print(f'   👨‍💼 {agent.name} ({agent.agent_id}) / agent123')
            
            return True
            
        except Exception as e:
            print(f'❌ Error migrating agent passwords: {e}')
            try:
                db.session.rollback()
            except:
                pass
            return False

if __name__ == "__main__":
    success = migrate_agent_passwords()
    if success:
        print('\n🎉 Agent authentication migration completed!')
        print('🚀 Agents can now login with proper password validation!')
    else:
        print('\n💥 Migration failed!')
