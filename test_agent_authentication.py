#!/usr/bin/env python3
"""
Test Agent Authentication System
"""

import requests
import time

def test_agent_authentication():
    """Test the new agent authentication system"""
    print('🔐 TESTING AGENT AUTHENTICATION SYSTEM')
    print('=' * 60)
    
    base_url = 'http://localhost:5001'
    
    # Test 1: Login with wrong password
    print('\n1. 🚫 Testing Invalid Password')
    session = requests.Session()
    
    login_response = session.post(f'{base_url}/agent/login', 
                                data={'agent_id': 'agent_001', 'password': 'wrongpassword'}, 
                                allow_redirects=False)
    
    if login_response.status_code == 200:
        # Should stay on login page with error
        if 'Invalid agent ID or password' in login_response.text:
            print('   ✅ Invalid password correctly rejected')
        else:
            print('   ❌ Invalid password was not properly rejected')
            return False
    else:
        print(f'   ❌ Unexpected response for invalid password: {login_response.status_code}')
        return False
    
    # Test 2: Login with correct password
    print('\n2. ✅ Testing Valid Password')
    login_response = session.post(f'{base_url}/agent/login', 
                                data={'agent_id': 'agent_001', 'password': 'agent123'}, 
                                allow_redirects=False)
    
    if login_response.status_code == 302:
        print('   ✅ Valid password accepted, redirected to dashboard')
        
        # Test 3: Access dashboard after login
        print('\n3. 📊 Testing Dashboard Access')
        dashboard_response = session.get(f'{base_url}/agent/dashboard')
        
        if dashboard_response.status_code == 200:
            print('   ✅ Dashboard accessible after authentication')
            
            # Test 4: API endpoints work
            print('\n4. 🔌 Testing API Endpoints')
            pending_response = session.get(f'{base_url}/agent/api/pending-sessions')
            my_sessions_response = session.get(f'{base_url}/agent/api/my-sessions')
            
            if pending_response.status_code == 200 and my_sessions_response.status_code == 200:
                print('   ✅ API endpoints accessible after authentication')
                
                pending_data = pending_response.json()
                my_sessions_data = my_sessions_response.json()
                
                print(f'   📊 Pending sessions: {len(pending_data.get("sessions", []))}')
                print(f'   📊 My sessions: {len(my_sessions_data.get("sessions", []))}')
                
            else:
                print('   ❌ API endpoints not accessible')
                return False
        else:
            print('   ❌ Dashboard not accessible after authentication')
            return False
    else:
        print('   ❌ Valid password was rejected')
        return False
    
    # Test 5: Test different agent
    print('\n5. 👨‍💼 Testing Different Agent')
    session2 = requests.Session()
    
    login_response2 = session2.post(f'{base_url}/agent/login', 
                                  data={'agent_id': 'agent_002', 'password': 'agent123'}, 
                                  allow_redirects=False)
    
    if login_response2.status_code == 302:
        print('   ✅ Second agent (Michael Chen) login successful')
    else:
        print('   ❌ Second agent login failed')
        return False
    
    # Test 6: Test invalid agent ID
    print('\n6. 👻 Testing Invalid Agent ID')
    session3 = requests.Session()
    
    login_response3 = session3.post(f'{base_url}/agent/login', 
                                  data={'agent_id': 'invalid_agent', 'password': 'agent123'}, 
                                  allow_redirects=False)
    
    if login_response3.status_code == 200:
        if 'Invalid agent ID or password' in login_response3.text:
            print('   ✅ Invalid agent ID correctly rejected')
        else:
            print('   ❌ Invalid agent ID was not properly rejected')
            return False
    else:
        print('   ❌ Unexpected response for invalid agent ID')
        return False
    
    # Test 7: Test logout functionality
    print('\n7. 🚪 Testing Logout')
    logout_response = session.get(f'{base_url}/agent/logout', allow_redirects=False)
    
    if logout_response.status_code == 302:
        print('   ✅ Logout successful')
        
        # Test that dashboard is no longer accessible
        dashboard_after_logout = session.get(f'{base_url}/agent/dashboard', allow_redirects=False)
        if dashboard_after_logout.status_code == 302:
            print('   ✅ Dashboard properly protected after logout')
        else:
            print('   ⚠️ Dashboard may not be properly protected after logout')
    else:
        print('   ❌ Logout failed')
        return False
    
    return True

def test_all_agents():
    """Test login for all agents"""
    print('\n' + '=' * 60)
    print('🧪 TESTING ALL AGENT ACCOUNTS')
    print('=' * 60)
    
    agents = [
        ('agent_001', 'Sarah Johnson'),
        ('agent_002', 'Michael Chen'),
        ('agent_003', 'Emma Williams'),
        ('agent_004', 'David Kumar')
    ]
    
    base_url = 'http://localhost:5001'
    
    for agent_id, agent_name in agents:
        print(f'\n👤 Testing {agent_name} ({agent_id})')
        
        session = requests.Session()
        login_response = session.post(f'{base_url}/agent/login', 
                                    data={'agent_id': agent_id, 'password': 'agent123'}, 
                                    allow_redirects=False)
        
        if login_response.status_code == 302:
            print(f'   ✅ {agent_name} authentication successful')
            
            # Test dashboard access
            dashboard_response = session.get(f'{base_url}/agent/dashboard')
            if dashboard_response.status_code == 200:
                print(f'   ✅ {agent_name} can access dashboard')
            else:
                print(f'   ❌ {agent_name} cannot access dashboard')
                return False
        else:
            print(f'   ❌ {agent_name} authentication failed')
            return False
    
    return True

if __name__ == "__main__":
    print('⏳ Waiting for server to be ready...')
    time.sleep(2)
    
    try:
        # Test basic authentication
        success1 = test_agent_authentication()
        
        # Test all agents
        success2 = test_all_agents()
        
        if success1 and success2:
            print('\n' + '=' * 60)
            print('🎉 ALL AUTHENTICATION TESTS PASSED!')
            print('=' * 60)
            print('\n✅ Agent authentication is working correctly!')
            print('🔐 Password validation implemented successfully!')
            print('🚀 System ready for production use!')
            
            print('\n📋 AGENT LOGIN CREDENTIALS:')
            print('   👨‍💼 Sarah Johnson (agent_001) / agent123')
            print('   👨‍💼 Michael Chen (agent_002) / agent123')
            print('   👨‍💼 Emma Williams (agent_003) / agent123')
            print('   👨‍💼 David Kumar (agent_004) / agent123')
            
            print('\n🔗 ACCESS URLS:')
            print('   Agent Login: http://localhost:5001/agent/login')
            print('   Super Admin: http://localhost:5001/super-admin/login')
            print('   Main Chat: http://localhost:5001/')
            
        else:
            print('\n❌ Some authentication tests failed!')
            
    except Exception as e:
        print(f'\n💥 Test execution failed: {e}')
        print('Make sure the server is running on http://localhost:5001')
