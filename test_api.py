#!/usr/bin/env python3
import requests
import time

print('Testing API endpoint...')
time.sleep(2)

# Test agent login
agent_session = requests.Session()
login_response = agent_session.post('http://localhost:5000/agent/login', 
                                  data={'agent_id': 'agent_001', 'password': 'any'}, 
                                  allow_redirects=False)

print(f'Login status: {login_response.status_code}')

if login_response.status_code == 302:
    # Test pending sessions API
    pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
    print(f'Pending sessions API status: {pending_response.status_code}')
    
    if pending_response.status_code != 200:
        print(f'Error response: {pending_response.text}')
    else:
        data = pending_response.json()
        print(f'Sessions found: {len(data.get("sessions", []))}')
        if data.get("sessions"):
            session = data["sessions"][0]
            print(f'Sample session keys: {list(session.keys())}')
