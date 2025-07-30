#!/usr/bin/env python3
"""
Create a test escalation manually for testing assignment
"""

from human_handoff.models import db, ChatSession, Message
from app import app
from datetime import datetime
import uuid

def create_test_escalation():
    """Create a test escalation manually"""
    print('🚨 Creating Test Escalation Manually')
    
    with app.app_context():
        try:
            # Create a test session
            session_id = str(uuid.uuid4())
            
            chat_session = ChatSession(
                session_id=session_id,
                user_id='test_user',
                requires_human=True,
                status='escalated',
                escalation_reason='Manual test escalation for assignment testing',
                escalated_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(chat_session)
            
            # Add a test message
            message = Message(
                session_id=session_id,
                sender_type='user',
                message_content='This is a test message for assignment testing',
                timestamp=datetime.utcnow()
            )
            
            db.session.add(message)
            db.session.commit()
            
            print(f'✅ Test escalation created: {session_id}')
            print(f'📋 Status: {chat_session.status}')
            print(f'📋 Requires Human: {chat_session.requires_human}')
            print(f'📋 Assigned Agent: {chat_session.assigned_agent_id}')
            
            return session_id
            
        except Exception as e:
            print(f'❌ Error creating test escalation: {e}')
            db.session.rollback()
            return None

if __name__ == "__main__":
    session_id = create_test_escalation()
    if session_id:
        print('\n🎯 Test escalation ready for assignment testing!')
    else:
        print('\n💥 Failed to create test escalation!')
