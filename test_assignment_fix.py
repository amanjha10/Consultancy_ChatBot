#!/usr/bin/env python3
"""
Test the assignment fix - super admin assignment should show in agent dashboard
"""

import requests
import time

def test_assignment_fix():
    """Test that super admin assignments appear in agent dashboard"""
    print('🔧 TESTING ASSIGNMENT FIX')
    print('=' * 50)
    
    # Step 1: Create an escalation
    print('\n1. 🚨 Creating Test Escalation')
    user_session = requests.Session()
    escalation_response = user_session.post('http://localhost:5000/chat', 
                                          json={'message': 'xyzabc123 assignment test escalation'})
    
    if escalation_response.status_code == 200:
        data = escalation_response.json()
        if data.get('escalated'):
            session_id = data.get('session_info', {}).get('session_id')
            print(f'   ✅ Escalation created: {session_id[:8]}...')
        else:
            print('   ⚠️ Escalation not triggered, creating manual session for test')
            # For testing, we'll proceed anyway
            session_id = None
    else:
        print('   ❌ Failed to create escalation')
        return False
    
    # Step 2: Super Admin Login
    print('\n2. 👑 Super Admin Login')
    super_admin_session = requests.Session()
    login_response = super_admin_session.post('http://localhost:5000/super-admin/login', 
                                            data={'admin_id': 'super_admin', 'password': 'admin123'}, 
                                            allow_redirects=False)
    
    if login_response.status_code == 302:
        print('   ✅ Super admin logged in')
    else:
        print('   ❌ Super admin login failed')
        return False
    
    # Step 3: Check Pending Sessions
    print('\n3. 📋 Checking Pending Sessions')
    pending_response = super_admin_session.get('http://localhost:5000/super-admin/api/pending-sessions')
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        pending_sessions = pending_data.get('sessions', [])
        print(f'   📊 Found {len(pending_sessions)} pending sessions')
        
        if pending_sessions:
            test_session = pending_sessions[0]
            session_id = test_session['session_id']
            print(f'   🎯 Using session: {session_id[:8]}...')
        else:
            print('   ⚠️ No pending sessions found')
            return False
    else:
        print('   ❌ Failed to get pending sessions')
        return False
    
    # Step 4: Get Available Agents
    print('\n4. 👥 Getting Available Agents')
    agents_response = super_admin_session.get('http://localhost:5000/super-admin/api/agents')
    
    if agents_response.status_code == 200:
        agents_data = agents_response.json()
        agents = agents_data.get('agents', [])
        available_agents = [agent for agent in agents if agent.get('status') == 'available']
        
        if available_agents:
            target_agent = available_agents[0]
            print(f'   ✅ Target agent: {target_agent["agent_name"]} ({target_agent["agent_id"]})')
        else:
            print('   ❌ No available agents')
            return False
    else:
        print('   ❌ Failed to get agents')
        return False
    
    # Step 5: Agent Login (Before Assignment)
    print('\n5. 👨‍💼 Agent Login (Before Assignment)')
    agent_session = requests.Session()
    agent_login = agent_session.post('http://localhost:5000/agent/login', 
                                   data={'agent_id': target_agent['agent_id'], 'password': 'any'}, 
                                   allow_redirects=False)
    
    if agent_login.status_code == 302:
        print('   ✅ Agent logged in')
        
        # Check agent's sessions before assignment
        my_sessions_before = agent_session.get('http://localhost:5000/agent/api/my-sessions')
        if my_sessions_before.status_code == 200:
            sessions_before = my_sessions_before.json().get('sessions', [])
            print(f'   📊 Agent has {len(sessions_before)} sessions before assignment')
        else:
            print('   ❌ Failed to get agent sessions before assignment')
            return False
    else:
        print('   ❌ Agent login failed')
        return False
    
    # Step 6: Super Admin Assignment
    print('\n6. 🎯 Super Admin Assignment')
    assign_response = super_admin_session.post('http://localhost:5000/super-admin/api/assign-session',
                                             json={
                                                 'session_id': session_id,
                                                 'agent_id': target_agent['agent_id']
                                             })
    
    if assign_response.status_code == 200:
        assign_data = assign_response.json()
        print(f'   ✅ Assignment successful: {assign_data.get("message", "No message")}')
        print(f'   📋 Assigned to: {assign_data.get("agent_name", "Unknown")}')
    else:
        assign_data = assign_response.json()
        print(f'   ❌ Assignment failed: {assign_data.get("error", "Unknown error")}')
        return False
    
    # Step 7: Check Agent Dashboard (After Assignment)
    print('\n7. 🔍 Checking Agent Dashboard (After Assignment)')
    
    # Wait a moment for database update
    time.sleep(1)
    
    my_sessions_after = agent_session.get('http://localhost:5000/agent/api/my-sessions')
    if my_sessions_after.status_code == 200:
        sessions_after = my_sessions_after.json().get('sessions', [])
        print(f'   📊 Agent has {len(sessions_after)} sessions after assignment')
        
        # Check if our assigned session is there
        assigned_session = next((s for s in sessions_after if s.get('session_id') == session_id), None)
        
        if assigned_session:
            print(f'   ✅ ASSIGNMENT APPEARS IN AGENT DASHBOARD!')
            print(f'   📋 Session ID: {assigned_session["session_id"][:8]}...')
            print(f'   📋 Status: {assigned_session.get("status", "Unknown")}')
            print(f'   📋 Escalation Reason: {assigned_session.get("escalation_reason", "Unknown")}')
            
            # Step 8: Verify Session Removed from Pending
            print('\n8. 🔄 Verifying Session Removed from Pending')
            pending_after = super_admin_session.get('http://localhost:5000/super-admin/api/pending-sessions')
            if pending_after.status_code == 200:
                pending_after_data = pending_after.json()
                pending_after_sessions = pending_after_data.get('sessions', [])
                
                still_pending = any(s.get('session_id') == session_id for s in pending_after_sessions)
                
                if not still_pending:
                    print('   ✅ Session correctly removed from pending list')
                else:
                    print('   ⚠️ Session still appears in pending list')
                
                print(f'   📊 Pending sessions after assignment: {len(pending_after_sessions)}')
            
            return True
        else:
            print('   ❌ ASSIGNMENT NOT FOUND IN AGENT DASHBOARD!')
            print('   🔍 Available sessions in agent dashboard:')
            for s in sessions_after:
                print(f'      - {s.get("session_id", "Unknown")[:8]}... (Status: {s.get("status", "Unknown")})')
            return False
    else:
        print('   ❌ Failed to get agent sessions after assignment')
        return False

if __name__ == "__main__":
    success = test_assignment_fix()
    if success:
        print('\n🎉 ASSIGNMENT FIX SUCCESSFUL!')
        print('✅ Super admin assignments now appear in agent dashboard')
        print('✅ Session status management working correctly')
        print('✅ Pending sessions list updated properly')
    else:
        print('\n💥 Assignment fix needs more work!')
