#!/usr/bin/env python3
"""
Setup initial data for the system
"""

from human_handoff.models import db, Agent, SuperAdmin
from app import app
from datetime import datetime

def setup_initial_data():
    """Setup initial agents and super admin"""
    with app.app_context():
        try:
            # Create super admin
            super_admin = SuperAdmin(
                admin_id='super_admin',
                name='System Administrator',
                email='admin@consultancy.com',
                password_hash='admin123',  # In production, this should be hashed
                created_at=datetime.utcnow()
            )
            db.session.add(super_admin)
            
            # Create initial agents
            agents = [
                {
                    'agent_id': 'agent_001',
                    'name': 'Sarah Johnson',
                    'email': 'sarah@consultancy.com',
                    'specialization': 'USA/Canada Education',
                    'max_concurrent_sessions': 3
                },
                {
                    'agent_id': 'agent_002',
                    'name': 'Michael Chen',
                    'email': 'michael@consultancy.com',
                    'specialization': 'UK/Europe Education',
                    'max_concurrent_sessions': 4
                },
                {
                    'agent_id': 'agent_003',
                    'name': 'Emma Williams',
                    'email': 'emma@consultancy.com',
                    'specialization': 'Australia/New Zealand',
                    'max_concurrent_sessions': 3
                },
                {
                    'agent_id': 'agent_004',
                    'name': 'David Kumar',
                    'email': 'david@consultancy.com',
                    'specialization': 'Scholarships & Financial Aid',
                    'max_concurrent_sessions': 5
                }
            ]
            
            for agent_data in agents:
                agent = Agent(
                    agent_id=agent_data['agent_id'],
                    name=agent_data['name'],
                    email=agent_data['email'],
                    specialization=agent_data['specialization'],
                    max_concurrent_sessions=agent_data['max_concurrent_sessions'],
                    status='offline',
                    current_sessions=0,
                    created_at=datetime.utcnow()
                )
                db.session.add(agent)
            
            db.session.commit()
            
            print('✅ Initial data setup completed successfully!')
            print(f'   👑 Super Admin: super_admin / admin123')
            print(f'   👨‍💼 Agents created: {len(agents)}')
            
            for agent_data in agents:
                print(f'      - {agent_data["name"]} ({agent_data["agent_id"]}) - {agent_data["specialization"]}')
            
        except Exception as e:
            print(f'❌ Error setting up initial data: {e}')
            db.session.rollback()

if __name__ == "__main__":
    setup_initial_data()
