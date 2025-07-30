#!/usr/bin/env python3
"""
Cleanup script to remove dummy/test sessions from the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from human_handoff.database import db
from human_handoff.models import ChatSession, Message, Agent, AgentSession
from datetime import datetime, timedelta

def cleanup_dummy_sessions():
    """Remove old test sessions and dummy data"""
    print("🧹 Cleaning up dummy sessions...")
    
    try:
        # Remove sessions older than 1 hour that are still pending
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Find old pending sessions
        old_sessions = ChatSession.query.filter(
            ChatSession.created_at < cutoff_time,
            ChatSession.status == 'escalated',
            ChatSession.assigned_agent_id.is_(None)
        ).all()
        
        print(f"Found {len(old_sessions)} old pending sessions to clean up")
        
        for session in old_sessions:
            print(f"Removing session: {session.session_id}")
            
            # Remove associated messages
            Message.query.filter_by(session_id=session.session_id).delete()
            
            # Remove the session
            db.session.delete(session)
        
        # Remove duplicate sessions (same session_id)
        duplicate_sessions = db.session.query(ChatSession.session_id).group_by(ChatSession.session_id).having(db.func.count(ChatSession.session_id) > 1).all()
        
        for (session_id,) in duplicate_sessions:
            sessions = ChatSession.query.filter_by(session_id=session_id).order_by(ChatSession.created_at.desc()).all()
            # Keep the newest, remove the rest
            for session in sessions[1:]:
                print(f"Removing duplicate session: {session.session_id}")
                Message.query.filter_by(session_id=session.session_id).delete()
                db.session.delete(session)
        
        # Remove orphaned messages (messages without sessions)
        orphaned_messages = db.session.query(Message).outerjoin(ChatSession, Message.session_id == ChatSession.session_id).filter(ChatSession.session_id.is_(None)).all()
        
        for message in orphaned_messages:
            print(f"Removing orphaned message: {message.id}")
            db.session.delete(message)
        
        # Remove old completed sessions (older than 24 hours)
        old_completed = ChatSession.query.filter(
            ChatSession.created_at < datetime.utcnow() - timedelta(hours=24),
            ChatSession.status == 'completed'
        ).all()
        
        for session in old_completed:
            print(f"Archiving old completed session: {session.session_id}")
            Message.query.filter_by(session_id=session.session_id).delete()
            db.session.delete(session)
        
        db.session.commit()
        print("✅ Cleanup completed successfully!")
        
        # Show current status
        remaining_pending = ChatSession.query.filter_by(status='escalated', assigned_agent_id=None).count()
        remaining_active = ChatSession.query.filter(ChatSession.assigned_agent_id.isnot(None)).count()
        
        print(f"📊 Current status:")
        print(f"   Pending sessions: {remaining_pending}")
        print(f"   Active sessions: {remaining_active}")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.session.rollback()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        cleanup_dummy_sessions()
