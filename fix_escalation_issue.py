#!/usr/bin/env python3
"""
Script to fix the escalation issue where simple greetings are being escalated to human agents
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from human_handoff import db
from human_handoff.models import ChatSession, Agent, Message
from app import app

def check_current_sessions():
    """Check current sessions and their status"""
    print("🔍 Checking current chat sessions...")
    
    with app.app_context():
        sessions = ChatSession.query.all()
        print(f"Found {len(sessions)} total sessions")
        
        escalated_sessions = ChatSession.query.filter_by(requires_human=True).all()
        print(f"Found {len(escalated_sessions)} escalated sessions")
        
        active_escalated = ChatSession.query.filter_by(status='escalated').all()
        print(f"Found {len(active_escalated)} sessions with 'escalated' status")
        
        for session in escalated_sessions:
            print(f"  - Session {session.session_id}: requires_human={session.requires_human}, status={session.status}, assigned_agent={session.assigned_agent_id}")
        
        return escalated_sessions

def reset_problematic_sessions():
    """Reset sessions that are incorrectly escalated"""
    print("\n🔧 Resetting problematic sessions...")
    
    with app.app_context():
        # Find sessions that are escalated but shouldn't be
        # (sessions with no messages or only greeting messages)
        
        problematic_sessions = []
        
        sessions = ChatSession.query.filter_by(requires_human=True).all()
        for session in sessions:
            messages = Message.query.filter_by(session_id=session.id).all()
            
            # Check if session has no messages or only greeting-type messages
            if len(messages) == 0:
                print(f"  - Found session with no messages: {session.session_id}")
                problematic_sessions.append(session)
            elif len(messages) <= 2:  # Only user message and maybe one bot response
                user_messages = [m for m in messages if m.sender == 'user']
                if len(user_messages) == 1:
                    user_msg = user_messages[0].content.lower().strip()
                    if any(greeting in user_msg for greeting in ['hey', 'hello', 'hi', 'good morning', 'good afternoon', 'good evening']):
                        print(f"  - Found session escalated for greeting: {session.session_id} - '{user_msg}'")
                        problematic_sessions.append(session)
        
        # Reset these sessions
        if problematic_sessions:
            print(f"\n🔄 Resetting {len(problematic_sessions)} problematic sessions...")
            for session in problematic_sessions:
                session.requires_human = False
                session.status = 'active'
                session.assigned_agent_id = None
                session.escalation_reason = None
                session.escalated_at = None
                print(f"  ✅ Reset session: {session.session_id}")
            
            db.session.commit()
            print("✅ All problematic sessions have been reset!")
        else:
            print("✅ No problematic sessions found!")

def clear_all_escalated_sessions():
    """Clear all escalated sessions (nuclear option)"""
    print("\n💥 NUCLEAR OPTION: Clearing ALL escalated sessions...")
    
    with app.app_context():
        escalated_sessions = ChatSession.query.filter_by(requires_human=True).all()
        
        if escalated_sessions:
            print(f"Found {len(escalated_sessions)} escalated sessions to reset")
            for session in escalated_sessions:
                session.requires_human = False
                session.status = 'active'
                session.assigned_agent_id = None
                session.escalation_reason = None
                session.escalated_at = None
                print(f"  ✅ Reset session: {session.session_id}")
            
            db.session.commit()
            print("✅ All escalated sessions have been reset!")
        else:
            print("✅ No escalated sessions found!")

def verify_fix():
    """Verify that the fix worked"""
    print("\n✅ Verifying fix...")
    
    with app.app_context():
        escalated_sessions = ChatSession.query.filter_by(requires_human=True).all()
        active_escalated = ChatSession.query.filter_by(status='escalated').all()
        
        print(f"Remaining escalated sessions (requires_human=True): {len(escalated_sessions)}")
        print(f"Remaining sessions with 'escalated' status: {len(active_escalated)}")
        
        if len(escalated_sessions) == 0 and len(active_escalated) == 0:
            print("🎉 SUCCESS: No escalated sessions remaining!")
            return True
        else:
            print("⚠️ WARNING: Some escalated sessions still remain")
            return False

if __name__ == "__main__":
    print("🚀 EduConsult Escalation Issue Fix")
    print("=" * 50)
    
    # Check current state
    escalated_sessions = check_current_sessions()
    
    if len(escalated_sessions) == 0:
        print("✅ No escalated sessions found. System looks good!")
        sys.exit(0)
    
    print(f"\n⚠️ Found {len(escalated_sessions)} escalated sessions that may be causing the issue.")
    
    choice = input("\nWhat would you like to do?\n1. Reset only problematic sessions (recommended)\n2. Reset ALL escalated sessions (nuclear option)\n3. Just show info and exit\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        reset_problematic_sessions()
        verify_fix()
    elif choice == "2":
        clear_all_escalated_sessions()
        verify_fix()
    elif choice == "3":
        print("ℹ️ Exiting without making changes")
    else:
        print("❌ Invalid choice. Exiting without making changes.")
    
    print("\n🏁 Done! You can now test the chatbot again.")
