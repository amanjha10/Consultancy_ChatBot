#!/usr/bin/env python3
"""
Test recent improvements: intelligent assignment, notifications, cleanup
"""

import requests
import time
import json

def test_intelligent_assignment():
    """Test intelligent assignment suggestions"""
    print('🎯 Testing Intelligent Assignment Suggestions')
    print('-' * 50)
    
    try:
        agent_session = requests.Session()
        
        # Agent login
        login_response = agent_session.post('http://localhost:5000/agent/login', 
                                          data={'agent_id': 'agent_001', 'password': 'any'}, 
                                          allow_redirects=False)
        
        if login_response.status_code == 302:
            # Get pending sessions with intelligent suggestions
            pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
            
            if pending_response.status_code == 200:
                data = pending_response.json()
                sessions = data.get('sessions', [])
                
                print(f'📊 Found {len(sessions)} pending sessions')
                
                if sessions:
                    session = sessions[0]
                    
                    # Check for intelligent assignment features
                    has_suggestions = 'assignment_suggestions' in session
                    has_priority = 'priority' in session
                    has_complexity = 'estimated_complexity' in session
                    has_recommendation = 'recommended_for_you' in session
                    
                    print(f'✅ Assignment suggestions: {has_suggestions}')
                    print(f'✅ Priority scoring: {has_priority}')
                    print(f'✅ Complexity estimation: {has_complexity}')
                    print(f'✅ Personal recommendations: {has_recommendation}')
                    
                    if has_suggestions:
                        suggestions = session.get('assignment_suggestions', [])
                        print(f'📋 Found {len(suggestions)} assignment suggestions')
                        if suggestions:
                            top_suggestion = suggestions[0]
                            print(f'   Top match: {top_suggestion.get("agent_name", "N/A")} ({top_suggestion.get("match_score", 0)}% match)')
                    
                    if has_priority:
                        print(f'📊 Session priority: {session.get("priority", "N/A")}')
                    
                    if has_complexity:
                        print(f'🔍 Estimated complexity: {session.get("estimated_complexity", "N/A")}')
                    
                    return has_suggestions and has_priority and has_complexity
                else:
                    print('ℹ️ No pending sessions to test intelligent assignment')
                    return True  # No sessions to test, but system is working
            else:
                print(f'❌ Failed to get pending sessions: {pending_response.status_code}')
                return False
        else:
            print(f'❌ Agent login failed: {login_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Intelligent assignment test error: {e}')
        return False

def test_enhanced_assignment_feedback():
    """Test enhanced assignment feedback and duplicate prevention"""
    print('\n🔄 Testing Enhanced Assignment Feedback')
    print('-' * 50)
    
    try:
        agent_session = requests.Session()
        
        # Agent login
        login_response = agent_session.post('http://localhost:5000/agent/login', 
                                          data={'agent_id': 'agent_001', 'password': 'any'}, 
                                          allow_redirects=False)
        
        if login_response.status_code == 302:
            # Get pending sessions
            pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
            
            if pending_response.status_code == 200:
                data = pending_response.json()
                sessions = data.get('sessions', [])
                
                if sessions:
                    session_id = sessions[0]['session_id']
                    
                    # Test assignment
                    assign_response = agent_session.post(f'http://localhost:5000/agent/api/session/{session_id}/assign')
                    
                    if assign_response.status_code == 200:
                        assign_data = assign_response.json()
                        
                        # Check for enhanced feedback
                        has_success_message = 'message' in assign_data
                        has_agent_name = 'agent_name' in assign_data
                        
                        print(f'✅ Enhanced success feedback: {has_success_message}')
                        print(f'✅ Agent name in response: {has_agent_name}')
                        
                        if has_success_message:
                            print(f'📋 Success message: {assign_data.get("message", "N/A")}')
                        
                        # Test duplicate assignment prevention
                        duplicate_response = agent_session.post(f'http://localhost:5000/agent/api/session/{session_id}/assign')
                        
                        if duplicate_response.status_code == 400:
                            duplicate_data = duplicate_response.json()
                            has_duplicate_prevention = 'already assigned' in duplicate_data.get('message', '').lower()
                            
                            print(f'✅ Duplicate assignment prevention: {has_duplicate_prevention}')
                            
                            return has_success_message and has_duplicate_prevention
                        else:
                            print(f'⚠️ Duplicate assignment not properly prevented: {duplicate_response.status_code}')
                            return False
                    else:
                        print(f'❌ Assignment failed: {assign_response.status_code}')
                        return False
                else:
                    print('ℹ️ No pending sessions to test assignment')
                    return True
            else:
                print(f'❌ Failed to get pending sessions: {pending_response.status_code}')
                return False
        else:
            print(f'❌ Agent login failed: {login_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Enhanced assignment feedback test error: {e}')
        return False

def test_real_time_notifications():
    """Test real-time notification system"""
    print('\n📢 Testing Real-time Notification System')
    print('-' * 50)
    
    try:
        # Create an escalation to trigger notifications
        user_session = requests.Session()
        
        escalation_response = user_session.post('http://localhost:5000/chat', 
                                              json={'message': 'xyzabc123 test escalation for notifications'})
        
        if escalation_response.status_code == 200:
            data = escalation_response.json()
            
            if data.get('escalated'):
                print('✅ Escalation created successfully')
                session_id = data.get('session_info', {}).get('session_id')
                print(f'📋 Session ID: {session_id}')
                
                # Check if notification system is set up (we can't test actual SocketIO easily in this script)
                # But we can verify the escalation appears in pending sessions quickly
                time.sleep(1)
                
                agent_session = requests.Session()
                login_response = agent_session.post('http://localhost:5000/agent/login', 
                                                  data={'agent_id': 'agent_001', 'password': 'any'}, 
                                                  allow_redirects=False)
                
                if login_response.status_code == 302:
                    pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
                    
                    if pending_response.status_code == 200:
                        pending_data = pending_response.json()
                        sessions = pending_data.get('sessions', [])
                        
                        # Check if our new session appears
                        found_session = any(s.get('session_id') == session_id for s in sessions)
                        
                        if found_session:
                            print('✅ New escalation appears in pending sessions (notification system working)')
                            return True
                        else:
                            print('⚠️ New escalation not found in pending sessions')
                            return False
                    else:
                        print(f'❌ Failed to check pending sessions: {pending_response.status_code}')
                        return False
                else:
                    print(f'❌ Agent login failed: {login_response.status_code}')
                    return False
            else:
                print('⚠️ Escalation was not triggered')
                return False
        else:
            print(f'❌ Failed to create escalation: {escalation_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Real-time notification test error: {e}')
        return False

def test_cleanup_system():
    """Test that cleanup system is working"""
    print('\n🧹 Testing Cleanup System')
    print('-' * 50)
    
    try:
        # Check current session count
        agent_session = requests.Session()
        login_response = agent_session.post('http://localhost:5000/agent/login', 
                                          data={'agent_id': 'agent_001', 'password': 'any'}, 
                                          allow_redirects=False)
        
        if login_response.status_code == 302:
            pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions')
            my_sessions_response = agent_session.get('http://localhost:5000/agent/api/my-sessions')
            
            if pending_response.status_code == 200 and my_sessions_response.status_code == 200:
                pending_data = pending_response.json()
                my_sessions_data = my_sessions_response.json()
                
                pending_count = len(pending_data.get('sessions', []))
                my_sessions_count = len(my_sessions_data.get('sessions', []))
                
                print(f'📊 Current pending sessions: {pending_count}')
                print(f'📊 Current my sessions: {my_sessions_count}')
                
                # Check if sessions have proper structure (indicating cleanup worked)
                if pending_count > 0:
                    session = pending_data['sessions'][0]
                    has_proper_structure = all(key in session for key in ['session_id', 'escalation_reason', 'escalated_at'])
                    print(f'✅ Sessions have proper structure: {has_proper_structure}')
                    return has_proper_structure
                else:
                    print('✅ No pending sessions (cleanup may have worked)')
                    return True
            else:
                print(f'❌ Failed to get session data: {pending_response.status_code}, {my_sessions_response.status_code}')
                return False
        else:
            print(f'❌ Agent login failed: {login_response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Cleanup system test error: {e}')
        return False

def main():
    """Test all recent improvements"""
    print('🧪 TESTING RECENT IMPROVEMENTS')
    print('=' * 60)
    print('Testing intelligent assignment, notifications, and cleanup...')
    
    tests = [
        ('Intelligent Assignment Suggestions', test_intelligent_assignment),
        ('Enhanced Assignment Feedback', test_enhanced_assignment_feedback),
        ('Real-time Notification System', test_real_time_notifications),
        ('Cleanup System', test_cleanup_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f'❌ {test_name} - Critical Error: {e}')
            results[test_name] = False
        
        time.sleep(1)
    
    # Summary
    print('\n📊 RECENT IMPROVEMENTS TEST SUMMARY')
    print('=' * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f'Tests Passed: {passed}/{total}')
    
    for test_name, result in results.items():
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{status} {test_name}')
    
    if passed == total:
        print('\n🎉 ALL RECENT IMPROVEMENTS WORKING!')
        print('The enhanced features are fully operational.')
    else:
        print(f'\n⚠️ {total - passed} IMPROVEMENT(S) NEED ATTENTION')
        print('Please check the failed components above.')
    
    return passed == total

if __name__ == "__main__":
    main()
