#!/usr/bin/env python3
"""
Test agent login functionality
"""

import requests

def test_agent_login():
    """Test agent login"""
    print("Testing agent login...")
    
    # Test login
    response = requests.post(
        'http://localhost:5000/agent/login',
        data={'agent_id': 'agent_001', 'password': 'any'},
        allow_redirects=False
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Location Header: {response.headers.get('Location', 'None')}")
    
    if response.status_code == 302 and '/agent/dashboard' in response.headers.get('Location', ''):
        print("✅ Login successful - redirected to dashboard")
        return True
    else:
        print("❌ Login failed")
        print(f"Response text: {response.text[:200]}...")
        return False

if __name__ == "__main__":
    test_agent_login()
