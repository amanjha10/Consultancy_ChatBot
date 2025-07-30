#!/usr/bin/env python3
"""
Quick verification script for Human Handoff System
Tests the basic functionality to ensure everything is working
"""

import requests
import json
import time

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🧪 Testing chat endpoint...")
    
    url = "http://localhost:5000/chat"
    
    # Test normal query
    normal_query = {
        "message": "What are the requirements for studying abroad?",
        "context": {}
    }
    
    try:
        response = requests.post(url, json=normal_query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Normal query successful")
            print(f"   Response: {data['response'][:100]}...")
        else:
            print(f"❌ Normal query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing normal query: {e}")
        return False
    
    # Test escalation query
    escalation_query = {
        "message": "I need help with something very complex that the bot cannot handle",
        "context": {}
    }
    
    try:
        response = requests.post(url, json=escalation_query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Escalation query successful")
            print(f"   Response type: {data.get('type', 'unknown')}")
            if data.get('escalated'):
                print("✅ Session escalated successfully")
            else:
                print("ℹ️  Session not escalated (may need more specific trigger)")
        else:
            print(f"❌ Escalation query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing escalation query: {e}")
        return False
    
    return True

def test_agent_endpoints():
    """Test agent dashboard endpoints"""
    print("\n🧪 Testing agent endpoints...")
    
    # Test agent login page
    try:
        response = requests.get("http://localhost:5000/agent/login", timeout=5)
        if response.status_code == 200:
            print("✅ Agent login page accessible")
        else:
            print(f"❌ Agent login page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing agent login: {e}")
        return False
    
    # Test agent dashboard (should redirect to login)
    try:
        response = requests.get("http://localhost:5000/agent/dashboard", timeout=5, allow_redirects=False)
        if response.status_code in [302, 401]:
            print("✅ Agent dashboard properly protected")
        else:
            print(f"⚠️  Agent dashboard response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing agent dashboard: {e}")
        return False
    
    return True

def test_static_files():
    """Test that static files are accessible"""
    print("\n🧪 Testing static files...")
    
    static_files = [
        "http://localhost:5000/static/style.css",
        "http://localhost:5000/static/script.js"
    ]
    
    for url in static_files:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url.split('/')[-1]} accessible")
            else:
                print(f"❌ {url.split('/')[-1]} failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error accessing {url}: {e}")
            return False
    
    return True

def check_server_running():
    """Check if the server is running"""
    print("🔍 Checking if server is running...")
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on http://localhost:5000")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Human Handoff System Verification")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("\n❌ Verification failed: Server not running")
        print("Please start the server with: python app.py")
        return False
    
    # Test chat functionality
    if not test_chat_endpoint():
        print("\n❌ Verification failed: Chat endpoint issues")
        return False
    
    # Test agent endpoints
    if not test_agent_endpoints():
        print("\n❌ Verification failed: Agent endpoint issues")
        return False
    
    # Test static files
    if not test_static_files():
        print("\n❌ Verification failed: Static file issues")
        return False
    
    print("\n🎉 All verification tests passed!")
    print("\n📋 System Status: ✅ WORKING")
    print("\n🚀 Ready to use:")
    print("   • User Chat: http://localhost:5000")
    print("   • Agent Dashboard: http://localhost:5000/agent/login")
    print("\n💡 Test escalation by asking:")
    print("   'I need help with something complex'")
    print("   'Sorry, I am unaware about this content'")
    
    return True

if __name__ == "__main__":
    main()
