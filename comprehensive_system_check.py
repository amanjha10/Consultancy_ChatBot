#!/usr/bin/env python3
"""
Comprehensive system check for all core functionalities
"""

import requests
import time
import json

def test_basic_connectivity():
    """Test basic server connectivity"""
    print('🔌 Testing Basic Connectivity')
    print('-' * 40)
    
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print('✅ Server is running and accessible')
            return True
        else:
            print(f'❌ Server returned status: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Cannot connect to server: {e}')
        return False

def test_rag_system():
    """Test RAG system functionality"""
    print('\n🧠 Testing RAG System')
    print('-' * 40)
    
    try:
        response = requests.post('http://localhost:5000/chat', 
                               json={'message': 'What are visa requirements?'}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data.get('response', '')) > 10:
                print('✅ RAG system working - got meaningful response')
                print(f'📄 Response preview: {data.get("response", "")[:100]}...')
                return True
            else:
                print('❌ RAG system returned empty/short response')
                print(f'📄 Full response: {data}')
                return False
        else:
            print(f'❌ RAG system failed: HTTP {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ RAG system error: {e}')
        return False

def test_popup_functionality():
    """Test popup/navigation functionality"""
    print('\n🎯 Testing Popup Functionality')
    print('-' * 40)
    
    try:
        # Test main menu
        response = requests.post('http://localhost:5000/chat', 
                               json={'message': 'Hello'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            if suggestions and len(suggestions) > 0:
                print('✅ Main menu working - got suggestions')
                print(f'📋 Suggestions: {suggestions[:3]}...')
            else:
                print('⚠️ Main menu working but no suggestions')
            
            # Test country selection
            country_response = requests.post('http://localhost:5000/chat', 
                                           json={'message': 'Choose Country'})
            
            if country_response.status_code == 200:
                country_data = country_response.json()
                country_suggestions = country_data.get('suggestions', [])
                if country_suggestions:
                    print('✅ Country selection working')
                    return True
                else:
                    print('⚠️ Country selection not returning suggestions')
                    return False
            else:
                print(f'❌ Country selection failed: {country_response.status_code}')
                return False
        else:
            print(f'❌ Main menu failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Popup functionality error: {e}')
        return False

def test_faq_admin():
    """Test FAQ admin functionality"""
    print('\n🔧 Testing FAQ Admin Panel')
    print('-' * 40)
    
    try:
        # Test admin page access
        response = requests.get('http://localhost:5000/admin/add-faq')
        if response.status_code == 200:
            print('✅ FAQ admin page accessible')
            
            # Test adding FAQ
            faq_data = {
                'category': 'general_queries.test',
                'question': f'Test FAQ at {time.strftime("%H:%M:%S")}',
                'answer': 'This is a test FAQ to verify the system is working.'
            }
            
            add_response = requests.post('http://localhost:5000/admin/add-faq', data=faq_data)
            if add_response.status_code == 200:
                print('✅ FAQ addition working')
                return True
            else:
                print(f'❌ FAQ addition failed: {add_response.status_code}')
                return False
        else:
            print(f'❌ FAQ admin page not accessible: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ FAQ admin error: {e}')
        return False

def test_agent_dashboard():
    """Test agent dashboard functionality"""
    print('\n👨‍💼 Testing Agent Dashboard')
    print('-' * 40)
    
    try:
        agent_session = requests.Session()
        
        # Test agent login page
        login_page = agent_session.get('http://localhost:5000/agent/login')
        if login_page.status_code != 200:
            print(f'❌ Agent login page not accessible: {login_page.status_code}')
            return False
        
        print('✅ Agent login page accessible')
        
        # Test agent login
        login_response = agent_session.post('http://localhost:5000/agent/login', 
                                          data={'agent_id': 'agent_001', 'password': 'any'}, 
                                          allow_redirects=False)
        
        if login_response.status_code == 302:
            print('✅ Agent login working')
            
            # Test dashboard access
            dashboard_response = agent_session.get('http://localhost:5000/agent/dashboard')
            if dashboard_response.status_code == 200:
                print('✅ Agent dashboard accessible')
                
                # Test API endpoints
                pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
                my_sessions_response = agent_session.get('http://localhost:5000/agent/api/my-sessions')
                
                if pending_response.status_code == 200 and my_sessions_response.status_code == 200:
                    print('✅ Agent API endpoints working')
                    
                    pending_data = pending_response.json()
                    my_sessions_data = my_sessions_response.json()
                    
                    print(f'📊 Pending sessions: {len(pending_data.get("sessions", []))}')
                    print(f'📊 My sessions: {len(my_sessions_data.get("sessions", []))}')
                    
                    return True
                else:
                    print(f'❌ Agent API endpoints failed: {pending_response.status_code}, {my_sessions_response.status_code}')
                    return False
            else:
                print(f'❌ Agent dashboard not accessible: {dashboard_response.status_code}')
                return False
        else:
            print(f'❌ Agent login failed: {login_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Agent dashboard error: {e}')
        return False

def test_human_handoff():
    """Test human handoff functionality"""
    print('\n🤝 Testing Human Handoff System')
    print('-' * 40)
    
    try:
        user_session = requests.Session()
        
        # Create escalation
        escalation_response = user_session.post('http://localhost:5000/chat', 
                                              json={'message': 'xyzabc123 nonsensical query to force escalation'})
        
        if escalation_response.status_code == 200:
            data = escalation_response.json()
            if data.get('escalated'):
                print('✅ Escalation working')
                session_id = data.get('session_info', {}).get('session_id')
                print(f'📋 Session escalated: {session_id}')
                
                # Test if escalated session appears in pending
                agent_session = requests.Session()
                agent_login = agent_session.post('http://localhost:5000/agent/login', 
                                                data={'agent_id': 'agent_001', 'password': 'any'}, 
                                                allow_redirects=False)
                
                if agent_login.status_code == 302:
                    pending_check = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
                    if pending_check.status_code == 200:
                        pending_data = pending_check.json()
                        sessions = pending_data.get('sessions', [])
                        
                        # Check if our session is in pending
                        found_session = any(s.get('session_id') == session_id for s in sessions)
                        if found_session:
                            print('✅ Escalated session appears in agent pending list')
                            return True
                        else:
                            print('⚠️ Escalated session not found in pending list')
                            print(f'📊 Found {len(sessions)} pending sessions')
                            return False
                    else:
                        print(f'❌ Could not check pending sessions: {pending_check.status_code}')
                        return False
                else:
                    print(f'❌ Agent login failed during handoff test: {agent_login.status_code}')
                    return False
            else:
                print('⚠️ Query did not trigger escalation')
                print(f'📄 Response: {data.get("response", "No response")}')
                return False
        else:
            print(f'❌ Escalation test failed: {escalation_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Human handoff error: {e}')
        return False

def main():
    """Run comprehensive system check"""
    print('🧪 COMPREHENSIVE SYSTEM CHECK')
    print('=' * 60)
    print('Testing all core functionalities and recent improvements...')
    
    tests = [
        ('Basic Connectivity', test_basic_connectivity),
        ('RAG System', test_rag_system),
        ('Popup Functionality', test_popup_functionality),
        ('FAQ Admin Panel', test_faq_admin),
        ('Agent Dashboard', test_agent_dashboard),
        ('Human Handoff System', test_human_handoff)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f'❌ {test_name} - Critical Error: {e}')
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print('\n📊 SYSTEM CHECK SUMMARY')
    print('=' * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f'Tests Passed: {passed}/{total}')
    
    for test_name, result in results.items():
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{status} {test_name}')
    
    if passed == total:
        print('\n🎉 ALL SYSTEMS WORKING CORRECTLY!')
        print('The Consultancy ChatBot is fully operational.')
    else:
        print(f'\n⚠️ {total - passed} SYSTEM(S) NEED ATTENTION')
        print('Please check the failed components above.')
    
    return passed == total

if __name__ == "__main__":
    main()
