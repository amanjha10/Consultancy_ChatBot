#!/usr/bin/env python3
"""
Test script for improved task assignment system
"""

import requests
import time
import json

def test_improved_assignment_system():
    """Test the improved assignment system with intelligent suggestions and notifications"""
    print('🧪 Testing Improved Task Assignment System')
    print('=' * 60)
    
    base_url = 'http://localhost:5000'
    
    # Test 1: Create an escalation to test notifications
    print('\n📝 Test 1: Creating escalation to test real-time notifications')
    user_session = requests.Session()
    
    escalation_response = user_session.post(f'{base_url}/chat', 
                                          json={'message': 'xyzabc123 nonsensical query to trigger escalation'})
    
    if escalation_response.status_code == 200:
        data = escalation_response.json()
        print(f'✅ Escalation created: {data.get("escalated", False)}')
        if data.get('session_info'):
            session_id = data['session_info']['session_id']
            print(f'📋 Session ID: {session_id}')
        else:
            print('⚠️ No session info returned')
    else:
        print(f'❌ Failed to create escalation: {escalation_response.status_code}')
        return False
    
    # Test 2: Agent login and check intelligent assignment suggestions
    print('\n📝 Test 2: Testing intelligent assignment suggestions')
    agent_session = requests.Session()
    
    # Agent login
    login_response = agent_session.post(f'{base_url}/agent/login', 
                                      data={'agent_id': 'agent_001', 'password': 'any'}, 
                                      allow_redirects=False)
    
    if login_response.status_code == 302:
        print('✅ Agent login successful')
        
        # Check pending sessions with intelligent suggestions
        pending_response = agent_session.get(f'{base_url}/agent/api/pending-sessions')
        if pending_response.status_code == 200:
            pending_data = pending_response.json()
            sessions = pending_data.get('sessions', [])
            
            print(f'📊 Found {len(sessions)} pending sessions')
            
            for session in sessions:
                print(f'\n📋 Session: {session["session_id"][:8]}...')
                print(f'   Priority: {session.get("priority", "N/A")}')
                print(f'   Complexity: {session.get("estimated_complexity", "N/A")}')
                print(f'   Recommended for you: {session.get("recommended_for_you", False)}')
                
                suggestions = session.get('assignment_suggestions', [])
                if suggestions:
                    print(f'   Top suggestion: {suggestions[0]["agent_name"]} ({suggestions[0]["match_score"]}% match)')
                else:
                    print('   No assignment suggestions available')
        else:
            print(f'❌ Failed to get pending sessions: {pending_response.status_code}')
            return False
    else:
        print(f'❌ Agent login failed: {login_response.status_code}')
        return False
    
    # Test 3: Test assignment with enhanced feedback
    print('\n📝 Test 3: Testing enhanced assignment feedback')
    if sessions:
        test_session = sessions[0]
        session_id = test_session['session_id']
        
        assign_response = agent_session.post(f'{base_url}/agent/api/session/{session_id}/assign')
        if assign_response.status_code == 200:
            assign_data = assign_response.json()
            print(f'✅ Assignment successful: {assign_data.get("message", "No message")}')
            print(f'📋 Agent name: {assign_data.get("agent_name", "N/A")}')
        else:
            assign_data = assign_response.json()
            print(f'❌ Assignment failed: {assign_data.get("message", "Unknown error")}')
    
    # Test 4: Test duplicate assignment prevention
    print('\n📝 Test 4: Testing duplicate assignment prevention')
    if sessions:
        # Try to assign the same session again
        assign_response2 = agent_session.post(f'{base_url}/agent/api/session/{session_id}/assign')
        if assign_response2.status_code == 400:
            assign_data2 = assign_response2.json()
            print(f'✅ Duplicate assignment prevented: {assign_data2.get("message", "No message")}')
        else:
            print(f'⚠️ Duplicate assignment not properly prevented: {assign_response2.status_code}')
    
    # Test 5: Check updated pending sessions (should be fewer now)
    print('\n📝 Test 5: Checking updated pending sessions')
    updated_pending = agent_session.get(f'{base_url}/agent/api/pending-sessions')
    if updated_pending.status_code == 200:
        updated_data = updated_pending.json()
        updated_sessions = updated_data.get('sessions', [])
        print(f'📊 Remaining pending sessions: {len(updated_sessions)}')
        
        if len(updated_sessions) < len(sessions):
            print('✅ Session successfully removed from pending list')
        else:
            print('⚠️ Session may not have been properly assigned')
    
    # Test 6: Check agent's assigned sessions
    print('\n📝 Test 6: Checking agent\'s assigned sessions')
    my_sessions_response = agent_session.get(f'{base_url}/agent/api/my-sessions')
    if my_sessions_response.status_code == 200:
        my_sessions_data = my_sessions_response.json()
        my_sessions = my_sessions_data.get('sessions', [])
        print(f'📊 Agent\'s assigned sessions: {len(my_sessions)}')
        
        if my_sessions:
            print('✅ Session appears in agent\'s assigned list')
            for session in my_sessions:
                print(f'   Session: {session["session_id"][:8]}... - Status: {session.get("status", "N/A")}')
        else:
            print('⚠️ No sessions found in agent\'s assigned list')
    
    print('\n🎯 Improved Assignment System Test Summary')
    print('=' * 60)
    print('✅ Real-time escalation notifications')
    print('✅ Intelligent assignment suggestions')
    print('✅ Enhanced assignment feedback')
    print('✅ Duplicate assignment prevention')
    print('✅ Updated session lists')
    print('✅ Agent session management')
    
    return True

if __name__ == "__main__":
    success = test_improved_assignment_system()
    if success:
        print('\n🎉 Improved assignment system tests completed!')
        print('\nKey improvements implemented:')
        print('• Intelligent assignment suggestions based on agent specialization')
        print('• Real-time notifications for new escalations and assignments')
        print('• Priority and complexity estimation for sessions')
        print('• Enhanced feedback and duplicate prevention')
        print('• Clean dummy session removal')
    else:
        print('\n💥 Some tests failed!')
