#!/usr/bin/env python3
"""
Debug integration issues
"""

import requests
import time

def debug_integration():
    print('🔍 Debugging Integration Issue')
    
    user_session = requests.Session()
    
    # Test escalation
    print('\n1. Testing escalation...')
    response = user_session.post('http://localhost:5000/chat', 
                               json={'message': 'I need complex help that requires human assistance'})
    
    if response.status_code == 200:
        data = response.json()
        print(f'Escalated: {data.get("escalated", False)}')
        print(f'Type: {data.get("type", "Unknown")}')
        print(f'Response: {data.get("response", "No response")[:100]}...')
        
        if data.get('escalated'):
            session_id = data.get('session_info', {}).get('session_id')
            print(f'Session ID: {session_id}')
            
            # Now have an agent take the session
            print('\n2. Agent taking session...')
            agent_session = requests.Session()
            login_response = agent_session.post('http://localhost:5000/agent/login', 
                                              data={'agent_id': 'agent_001', 'password': 'any'}, 
                                              allow_redirects=False)
            
            if login_response.status_code == 302:
                print('Agent logged in successfully')
                
                # Get pending sessions
                pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
                if pending_response.status_code == 200:
                    pending_data = pending_response.json()
                    sessions = pending_data.get('sessions', [])
                    print(f'Pending sessions: {len(sessions)}')
                    
                    # Find our session and assign it
                    target_session = None
                    for session in sessions:
                        if session.get('session_id') == session_id:
                            target_session = session
                            break
                    
                    if target_session:
                        print(f'Found target session: {session_id}')
                        
                        # Assign session
                        assign_response = agent_session.post(f'http://localhost:5000/agent/api/session/{session_id}/assign')
                        if assign_response.status_code == 200:
                            print('Session assigned to agent')
                            
                            # Wait a moment
                            time.sleep(2)
                            
                            # Test follow-up
                            print('\n3. Testing follow-up message...')
                            follow_up = user_session.post('http://localhost:5000/chat', 
                                                         json={'message': 'Are you there?'})
                            
                            if follow_up.status_code == 200:
                                follow_data = follow_up.json()
                                print(f'Follow-up type: {follow_data.get("type", "Unknown")}')
                                print(f'Follow-up response: {follow_data.get("response", "No response")}')
                                
                                if follow_data.get('type') == 'human_handling':
                                    print('✅ Integration working correctly!')
                                    return True
                                else:
                                    print('❌ Human handoff not working properly')
                                    return False
                            else:
                                print(f'Follow-up failed: {follow_up.status_code}')
                                return False
                        else:
                            print(f'Session assignment failed: {assign_response.status_code}')
                            return False
                    else:
                        print('Target session not found in pending sessions')
                        return False
                else:
                    print(f'Failed to get pending sessions: {pending_response.status_code}')
                    return False
            else:
                print(f'Agent login failed: {login_response.status_code}')
                return False
        else:
            print('Escalation did not occur')
            return False
    else:
        print(f'Initial request failed: {response.status_code}')
        return False

if __name__ == "__main__":
    success = debug_integration()
    if success:
        print('\n🎉 Integration is working correctly!')
    else:
        print('\n💥 Integration needs fixing!')
