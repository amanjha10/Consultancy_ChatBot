#!/usr/bin/env python3
"""
Test real-time messaging between agent and user
"""

import requests
import time

def test_escalation_and_agent_response():
    """Test the complete flow: escalation -> agent assignment -> agent message"""
    print("🧪 Testing real-time messaging flow...")
    
    # Step 1: Create a session and trigger escalation
    print("\n1. Triggering escalation...")
    escalation_response = requests.post(
        'http://localhost:5000/chat',
        json={'message': 'I need help with something very complex that the bot cannot handle'},
        timeout=10
    )
    
    if escalation_response.status_code != 200:
        print(f"❌ Escalation failed: {escalation_response.status_code}")
        return False
    
    escalation_data = escalation_response.json()
    print(f"✅ Escalation response: {escalation_data.get('type', 'unknown')}")
    
    if not escalation_data.get('escalated'):
        print("❌ Session was not escalated")
        return False
    
    session_info = escalation_data.get('session_info', {})
    session_id = session_info.get('session_id')
    
    if not session_id:
        print("❌ No session ID found")
        return False
    
    print(f"✅ Session escalated: {session_id}")
    
    # Step 2: Login as agent
    print("\n2. Logging in as agent...")
    login_response = requests.post(
        'http://localhost:5000/agent/login',
        data={'agent_id': 'agent_001', 'password': 'any'},
        allow_redirects=False
    )
    
    if login_response.status_code != 302:
        print(f"❌ Agent login failed: {login_response.status_code}")
        return False
    
    # Get session cookies
    cookies = login_response.cookies
    print("✅ Agent logged in successfully")
    
    # Step 3: Check pending sessions
    print("\n3. Checking pending sessions...")
    pending_response = requests.get(
        'http://localhost:5000/agent/api/pending-sessions',
        cookies=cookies,
        timeout=5
    )
    
    if pending_response.status_code != 200:
        print(f"❌ Failed to get pending sessions: {pending_response.status_code}")
        return False
    
    pending_data = pending_response.json()
    pending_sessions = pending_data.get('sessions', [])
    
    # Find our session
    our_session = None
    for session in pending_sessions:
        if session['session_id'] == session_id:
            our_session = session
            break
    
    if not our_session:
        print(f"❌ Session {session_id} not found in pending sessions")
        print(f"Available sessions: {[s['session_id'] for s in pending_sessions]}")
        return False
    
    print(f"✅ Found pending session: {session_id}")
    
    # Step 4: Assign session to agent
    print("\n4. Assigning session to agent...")
    assign_response = requests.post(
        f'http://localhost:5000/agent/api/session/{session_id}/assign',
        cookies=cookies,
        timeout=5
    )
    
    if assign_response.status_code != 200:
        print(f"❌ Failed to assign session: {assign_response.status_code}")
        return False
    
    assign_data = assign_response.json()
    if not assign_data.get('success'):
        print(f"❌ Session assignment failed: {assign_data.get('message')}")
        return False
    
    print("✅ Session assigned to agent")
    
    # Step 5: Send message as agent
    print("\n5. Sending message as agent...")
    message_response = requests.post(
        f'http://localhost:5000/agent/api/session/{session_id}/send-message',
        json={'message': 'Hello! I am a human agent. How can I help you today?'},
        cookies=cookies,
        timeout=5
    )
    
    if message_response.status_code != 200:
        print(f"❌ Failed to send agent message: {message_response.status_code}")
        return False
    
    message_data = message_response.json()
    if not message_data.get('success'):
        print(f"❌ Agent message failed: {message_data.get('message')}")
        return False
    
    print("✅ Agent message sent successfully")
    print(f"   Message: {message_data.get('message', {}).get('message_content', 'N/A')}")
    
    # Step 6: Verify message was saved
    print("\n6. Verifying message was saved...")
    messages_response = requests.get(
        f'http://localhost:5000/agent/api/session/{session_id}/messages',
        cookies=cookies,
        timeout=5
    )
    
    if messages_response.status_code != 200:
        print(f"❌ Failed to get messages: {messages_response.status_code}")
        return False
    
    messages_data = messages_response.json()
    messages = messages_data.get('messages', [])
    
    # Find agent message
    agent_messages = [msg for msg in messages if msg['sender_type'] == 'agent']
    
    if not agent_messages:
        print("❌ No agent messages found")
        return False
    
    print(f"✅ Found {len(agent_messages)} agent message(s)")
    print(f"   Latest: {agent_messages[-1]['message_content']}")
    
    return True

if __name__ == "__main__":
    success = test_escalation_and_agent_response()
    if success:
        print("\n🎉 Real-time messaging test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Open user chat: http://localhost:5000")
        print("2. Open agent dashboard: http://localhost:5000/agent/login")
        print("3. Test real-time messaging manually")
    else:
        print("\n❌ Real-time messaging test failed")
        print("Check the server logs for more details")
