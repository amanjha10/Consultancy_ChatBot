#!/usr/bin/env python3
"""
Diagnose current system issues
"""

import requests
import time

def diagnose_system():
    """Diagnose all current system issues"""
    print('🔍 DIAGNOSING CURRENT SYSTEM ISSUES')
    print('=' * 60)
    
    issues = []
    
    # Test 1: Basic connectivity
    print('\n1. 🌐 Testing Basic Connectivity')
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print('   ✅ Server accessible')
        else:
            print(f'   ❌ Server returned {response.status_code}')
            issues.append('Server connectivity issue')
    except Exception as e:
        print(f'   ❌ Server not accessible: {e}')
        issues.append('Server not running')
        return issues
    
    # Test 2: Core chatbot functionality
    print('\n2. 🤖 Testing Core Chatbot')
    try:
        chat_response = requests.post('http://localhost:5000/chat', 
                                    json={'message': 'Hello'}, timeout=10)
        if chat_response.status_code == 200:
            data = chat_response.json()
            if data.get('response'):
                print('   ✅ Chatbot responding')
            else:
                print('   ❌ Chatbot not responding properly')
                issues.append('Chatbot response issue')
        else:
            print(f'   ❌ Chat endpoint returned {chat_response.status_code}')
            issues.append('Chat endpoint issue')
    except Exception as e:
        print(f'   ❌ Chat test failed: {e}')
        issues.append('Chat functionality broken')
    
    # Test 3: Agent login
    print('\n3. 👨‍💼 Testing Agent Login')
    agent_session = requests.Session()
    try:
        login_response = agent_session.post('http://localhost:5000/agent/login',
                                          data={'agent_id': 'agent_001', 'password': 'any'},
                                          allow_redirects=False, timeout=10)
        if login_response.status_code == 302:
            print('   ✅ Agent login working')
            
            # Test agent dashboard access
            dashboard_response = agent_session.get('http://localhost:5000/agent/dashboard', timeout=10)
            if dashboard_response.status_code == 200:
                print('   ✅ Agent dashboard accessible')
                
                # Test API endpoints
                pending_response = agent_session.get('http://localhost:5000/agent/api/pending-sessions', timeout=10)
                my_sessions_response = agent_session.get('http://localhost:5000/agent/api/my-sessions', timeout=10)
                
                if pending_response.status_code == 200:
                    print('   ✅ Pending sessions API working')
                else:
                    print(f'   ❌ Pending sessions API failed: {pending_response.status_code}')
                    issues.append('Agent pending sessions API broken')
                
                if my_sessions_response.status_code == 200:
                    print('   ✅ My sessions API working')
                else:
                    print(f'   ❌ My sessions API failed: {my_sessions_response.status_code}')
                    issues.append('Agent my sessions API broken')
            else:
                print(f'   ❌ Agent dashboard not accessible: {dashboard_response.status_code}')
                issues.append('Agent dashboard broken')
        else:
            print(f'   ❌ Agent login failed: {login_response.status_code}')
            issues.append('Agent login broken')
    except Exception as e:
        print(f'   ❌ Agent test failed: {e}')
        issues.append('Agent system broken')
    
    # Test 4: Super Admin login
    print('\n4. 👑 Testing Super Admin Login')
    super_admin_session = requests.Session()
    try:
        super_login_response = super_admin_session.post('http://localhost:5000/super-admin/login',
                                                       data={'admin_id': 'super_admin', 'password': 'admin123'},
                                                       allow_redirects=False, timeout=10)
        if super_login_response.status_code == 302:
            print('   ✅ Super admin login working')
            
            # Test super admin dashboard
            super_dashboard_response = super_admin_session.get('http://localhost:5000/super-admin/dashboard', timeout=10)
            if super_dashboard_response.status_code == 200:
                print('   ✅ Super admin dashboard accessible')
                
                # Test super admin APIs
                super_pending_response = super_admin_session.get('http://localhost:5000/super-admin/api/pending-sessions', timeout=10)
                super_agents_response = super_admin_session.get('http://localhost:5000/super-admin/api/agents', timeout=10)
                
                if super_pending_response.status_code == 200:
                    print('   ✅ Super admin pending sessions API working')
                else:
                    print(f'   ❌ Super admin pending sessions API failed: {super_pending_response.status_code}')
                    issues.append('Super admin pending sessions API broken')
                
                if super_agents_response.status_code == 200:
                    agents_data = super_agents_response.json()
                    agents = agents_data.get('agents', [])
                    print(f'   ✅ Super admin agents API working ({len(agents)} agents)')
                    
                    # Check agent status tracking
                    active_agents = [a for a in agents if a.get('status') == 'available']
                    print(f'   📊 Available agents: {len(active_agents)}')
                    
                    if len(agents) == 0:
                        issues.append('No agents found in system')
                else:
                    print(f'   ❌ Super admin agents API failed: {super_agents_response.status_code}')
                    issues.append('Super admin agents API broken')
            else:
                print(f'   ❌ Super admin dashboard not accessible: {super_dashboard_response.status_code}')
                issues.append('Super admin dashboard broken')
        else:
            print(f'   ❌ Super admin login failed: {super_login_response.status_code}')
            issues.append('Super admin login broken')
    except Exception as e:
        print(f'   ❌ Super admin test failed: {e}')
        issues.append('Super admin system broken')
    
    # Test 5: FAQ Admin
    print('\n5. 🔧 Testing FAQ Admin')
    try:
        faq_response = requests.get('http://localhost:5000/admin/add-faq', timeout=10)
        if faq_response.status_code == 200:
            print('   ✅ FAQ admin accessible')
        else:
            print(f'   ❌ FAQ admin not accessible: {faq_response.status_code}')
            issues.append('FAQ admin broken')
    except Exception as e:
        print(f'   ❌ FAQ admin test failed: {e}')
        issues.append('FAQ admin broken')
    
    # Test 6: Database connectivity
    print('\n6. 🗄️ Testing Database')
    try:
        # Test by trying to get agents through super admin API
        if super_admin_session:
            agents_test = super_admin_session.get('http://localhost:5000/super-admin/api/agents', timeout=10)
            if agents_test.status_code == 200:
                print('   ✅ Database connectivity working')
            else:
                print('   ❌ Database connectivity issue')
                issues.append('Database connectivity problem')
    except Exception as e:
        print(f'   ❌ Database test failed: {e}')
        issues.append('Database broken')
    
    # Summary
    print('\n' + '=' * 60)
    print('📊 DIAGNOSIS SUMMARY')
    print('=' * 60)
    
    if issues:
        print(f'\n❌ FOUND {len(issues)} ISSUES:')
        for i, issue in enumerate(issues, 1):
            print(f'   {i}. {issue}')
    else:
        print('\n✅ NO ISSUES FOUND - SYSTEM APPEARS HEALTHY')
    
    return issues

if __name__ == "__main__":
    issues = diagnose_system()
    if issues:
        print('\n🔧 ISSUES NEED TO BE FIXED!')
    else:
        print('\n🎉 SYSTEM IS WORKING CORRECTLY!')
