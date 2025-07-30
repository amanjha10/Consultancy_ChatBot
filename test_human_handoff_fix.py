#!/usr/bin/env python3
"""
Test script to verify the human handoff fix is working correctly.
This script tests that the bot does not respond when a human agent is handling the session.
"""

import requests
import time

def test_human_handoff_fix():
    """Test the human handoff fix"""
    print("🧪 Testing Human Handoff Fix")
    print("=" * 50)
    
    # Create a session object to maintain cookies
    user_session = requests.Session()
    
    # Step 1: Create escalation
    print("\n📝 Step 1: Creating escalation...")
    response = user_session.post('http://localhost:5000/chat', 
                                json={'message': 'I need help with something very complex that requires human assistance'})
    
    if response.status_code != 200:
        print(f"❌ Failed to create escalation: {response.status_code}")
        return False
        
    data = response.json()
    escalated = data.get('escalated', False)
    session_id = data.get('session_info', {}).get('session_id')
    
    print(f"   Escalated: {escalated}")
    print(f"   Session ID: {session_id}")
    
    if not escalated:
        print("❌ Session was not escalated")
        return False
    
    # Step 2: Agent takes the session
    print("\n👨‍💼 Step 2: Agent taking session...")
    agent_session = requests.Session()
    
    # Agent login
    login_response = agent_session.post('http://localhost:5000/agent/login', 
                                       data={'agent_id': 'agent_001', 'password': 'any'}, 
                                       allow_redirects=False)
    
    if login_response.status_code != 302:
        print(f"❌ Agent login failed: {login_response.status_code}")
        return False
    
    # Get pending sessions
    pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
    pending_data = pending_response.json()
    pending_sessions = pending_data.get('sessions', [])
    
    print(f"   Pending sessions found: {len(pending_sessions)}")
    
    if not pending_sessions:
        print("❌ No pending sessions found")
        return False
    
    # Find our session
    target_session = None
    for session in pending_sessions:
        if session.get('session_id') == session_id:
            target_session = session
            break
    
    if not target_session:
        print(f"❌ Target session {session_id} not found in pending sessions")
        return False
    
    # Assign session to agent
    assign_response = agent_session.post(f'http://localhost:5000/agent/api/session/{session_id}/assign')
    
    if assign_response.status_code != 200:
        print(f"❌ Failed to assign session: {assign_response.status_code}")
        return False
    
    print(f"   ✅ Session {session_id} assigned to agent")
    
    # Wait a moment for the assignment to be processed
    time.sleep(1)
    
    # Step 3: Test the fix - user tries to send message while human is handling
    print("\n🤖 Step 3: Testing bot response when human is handling...")
    response = user_session.post('http://localhost:5000/chat', 
                                json={'message': 'Hello, are you there? Can you help me?'})
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        return False
    
    data = response.json()
    response_type = data.get('type')
    bot_response = data.get('response', '')
    escalated_flag = data.get('escalated', False)
    
    print(f"   Response type: {response_type}")
    print(f"   Bot response: {repr(bot_response)}")
    print(f"   Escalated flag: {escalated_flag}")
    
    # Check if the fix is working
    if response_type == 'human_handling':
        print("\n✅ SUCCESS: Bot correctly detected human is handling and did not respond!")
        print("   The fix is working correctly.")
        return True
    else:
        print("\n❌ FAILURE: Bot responded even though human should be handling")
        print(f"   Expected type: 'human_handling', got: '{response_type}'")
        print(f"   Full response: {data}")
        return False

if __name__ == "__main__":
    try:
        success = test_human_handoff_fix()
        if success:
            print("\n🎉 All tests passed! The human handoff fix is working correctly.")
        else:
            print("\n💥 Test failed! The fix needs more work.")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
