#!/usr/bin/env python3
"""
Create default agents for the system
"""

from human_handoff.models import db, Agent
from app import app
from datetime import datetime

def create_default_agents():
    """Create default agents"""
    print('👥 Creating default agents...')
    
    with app.app_context():
        try:
            # Check if agents already exist
            existing_agents = Agent.query.count()
            if existing_agents > 0:
                print(f'✅ {existing_agents} agents already exist')
                return True
            
            # Create default agents
            agents_data = [
                {
                    'agent_id': 'agent_001',
                    'name': 'Sarah Johnson',
                    'email': 'sarah@educonsult.com',
                    'specialization': 'visa',
                    'max_concurrent_sessions': 5,
                    'status': 'available'
                },
                {
                    'agent_id': 'agent_002',
                    'name': 'Michael Chen',
                    'email': 'michael@educonsult.com',
                    'specialization': 'scholarships',
                    'max_concurrent_sessions': 4,
                    'status': 'available'
                },
                {
                    'agent_id': 'agent_003',
                    'name': 'Emma Wilson',
                    'email': 'emma@educonsult.com',
                    'specialization': 'general',
                    'max_concurrent_sessions': 6,
                    'status': 'available'
                }
            ]
            
            for agent_data in agents_data:
                agent = Agent(
                    agent_id=agent_data['agent_id'],
                    name=agent_data['name'],
                    email=agent_data['email'],
                    specialization=agent_data['specialization'],
                    max_concurrent_sessions=agent_data['max_concurrent_sessions'],
                    status=agent_data['status'],
                    is_active=True,
                    last_active=datetime.utcnow()
                )
                db.session.add(agent)
                print(f'✅ Created agent: {agent.name} ({agent.specialization})')
            
            db.session.commit()
            print('✅ All default agents created successfully!')
            return True
            
        except Exception as e:
            print(f'❌ Error creating agents: {e}')
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = create_default_agents()
    if success:
        print('\n🎉 Default agents ready!')
    else:
        print('\n💥 Failed to create default agents!')
