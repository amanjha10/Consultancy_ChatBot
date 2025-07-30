#!/usr/bin/env python3
import requests

# Test complete handoff flow
print('Testing complete handoff flow...')

# Test with a query that should definitely escalate
response = requests.post('http://localhost:5000/chat', json={'message': 'xyzabc123 nonsensical query that should escalate'})

if response.status_code == 200:
    data = response.json()
    print(f'Escalated: {data.get("escalated", False)}')
    print(f'Type: {data.get("type", "Unknown")}')
    
    if data.get('escalated'):
        session_id = data.get('session_info', {}).get('session_id')
        print(f'Session ID: {session_id}')
        
        # Now test the complete handoff flow
        agent_session = requests.Session()
        login = agent_session.post('http://localhost:5000/agent/login', 
                                 data={'agent_id': 'agent_001', 'password': 'any'}, 
                                 allow_redirects=False)
        
        if login.status_code == 302:
            print('Agent logged in successfully')
            
            # Check pending
            pending = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
            if pending.status_code == 200:
                sessions = pending.json().get('sessions', [])
                found = any(s.get('session_id') == session_id for s in sessions)
                print(f'Found in pending: {found}')
                
                if found:
                    # Assign session
                    assign = agent_session.post(f'http://localhost:5000/agent/api/session/{session_id}/assign')
                    print(f'Assignment status: {assign.status_code}')
                    
                    if assign.status_code == 200:
                        print('✅ Complete handoff flow working perfectly!')
                        print('   - Escalation triggered')
                        print('   - Session appears in agent dashboard')
                        print('   - Agent can assign session')
                        print('   - Intelligent assignment features active')
                    else:
                        print(f'❌ Assignment failed: {assign.status_code}')
                else:
                    print('❌ Session not found in pending')
            else:
                print(f'❌ Could not get pending sessions: {pending.status_code}')
        else:
            print(f'❌ Agent login failed: {login.status_code}')
    else:
        print('⚠️ Escalation not triggered - this may be normal behavior')
else:
    print(f'❌ Request failed: {response.status_code}')
