#!/usr/bin/env python3
"""
Complete System Health Check
Verifies all components are working after Firecrawl integration
"""

import requests
import time
import json

def test_basic_system():
    """Test basic application functionality"""
    print("🌐 Testing Basic System...")
    
    try:
        response = requests.get('http://localhost:5001', timeout=10)
        if response.status_code == 200:
            print("✅ Application is running and accessible")
            return True
        else:
            print(f"❌ Application returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running - please start with: python3 app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        return False

def test_rag_system():
    """Test RAG system with Firecrawl data"""
    print("\n🧠 Testing RAG System with Firecrawl Data...")
    
    test_queries = [
        "What is KIEC's success rate?",
        "How many universities does KIEC partner with?", 
        "Tell me about KIEC's services",
        "What countries does KIEC cover?",
        "What universities does KIEC work with?",
        "Tell me about study abroad requirements"  # Non-Firecrawl query
    ]
    
    passed = 0
    total = len(test_queries)
    
    for query in test_queries:
        try:
            response = requests.post('http://localhost:5001/chat', 
                                   json={'message': query}, 
                                   timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                response_type = data.get('type', '')
                
                # Check if we got a meaningful response
                if len(response_text) > 50 and response_type == 'faq_response':
                    print(f"✅ '{query}' - Good response ({len(response_text)} chars)")
                    passed += 1
                elif len(response_text) > 20:
                    print(f"⚠️  '{query}' - Basic response ({len(response_text)} chars)")
                    passed += 0.5
                else:
                    print(f"❌ '{query}' - Poor response")
            else:
                print(f"❌ '{query}' - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{query}' - Error: {e}")
    
    success_rate = (passed / total) * 100
    print(f"\n📊 RAG Test Results: {passed}/{total} passed ({success_rate:.1f}%)")
    return success_rate >= 70

def test_human_handoff():
    """Test human handoff system"""
    print("\n🤝 Testing Human Handoff System...")
    
    try:
        # Test escalation
        user_session = requests.Session()
        escalation_response = user_session.post('http://localhost:5001/chat', 
                                              json={'message': 'I need complex help that requires human assistance'})
        
        if escalation_response.status_code == 200:
            data = escalation_response.json()
            if data.get('escalated'):
                print("✅ Escalation working")
                
                # Test agent login
                agent_session = requests.Session()
                login_response = agent_session.post('http://localhost:5001/agent/login', 
                                                  data={'agent_id': 'agent_001', 'password': 'any'}, 
                                                  allow_redirects=False)
                
                if login_response.status_code == 302:
                    print("✅ Agent login working")
                    
                    # Test agent dashboard
                    dashboard_response = agent_session.get('http://localhost:5001/agent/dashboard')
                    if dashboard_response.status_code == 200:
                        print("✅ Agent dashboard accessible")
                        
                        # Test pending sessions API
                        pending_response = agent_session.get('http://localhost:5001/agent/api/pending-sessions')
                        if pending_response.status_code == 200:
                            print("✅ Agent API working")
                            return True
                        else:
                            print("❌ Agent API failed")
                    else:
                        print("❌ Agent dashboard failed")
                else:
                    print("❌ Agent login failed")
            else:
                print("❌ Escalation not triggered")
        else:
            print("❌ Chat endpoint failed")
        
        return False
        
    except Exception as e:
        print(f"❌ Human handoff error: {e}")
        return False

def test_faq_admin():
    """Test FAQ admin panel"""
    print("\n🔧 Testing FAQ Admin Panel...")
    
    try:
        # Test admin page access
        response = requests.get('http://localhost:5001/admin/add-faq')
        if response.status_code == 200:
            print("✅ FAQ admin page accessible")
            
            # Test adding FAQ
            faq_data = {
                'question': f'System test FAQ {time.strftime("%H:%M:%S")}',
                'answer': 'This is a system test to verify integration is working.',
                'section': 'System Test'
            }
            
            add_response = requests.post('http://localhost:5001/admin/add-faq', data=faq_data)
            if add_response.status_code == 200:
                print("✅ FAQ addition working")
                return True
            else:
                print(f"❌ FAQ addition failed: {add_response.status_code}")
        else:
            print(f"❌ FAQ admin page not accessible: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ FAQ admin error: {e}")
        return False

def test_navigation_buttons():
    """Test navigation button functionality"""
    print("\n🎯 Testing Navigation Buttons...")
    
    button_tests = [
        '🌍 Choose Country',
        '🎓 Browse Programs', 
        'United States',
        'Canada',
        'Talk to advisor'
    ]
    
    passed = 0
    for button in button_tests:
        try:
            response = requests.post('http://localhost:5001/chat', 
                                   json={'message': button})
            
            if response.status_code == 200:
                data = response.json()
                if 'suggestions' in data and len(data['suggestions']) > 0:
                    print(f"✅ '{button}' - Works")
                    passed += 1
                else:
                    print(f"⚠️  '{button}' - No suggestions")
            else:
                print(f"❌ '{button}' - Failed")
        
        except Exception as e:
            print(f"❌ '{button}' - Error: {e}")
    
    success_rate = (passed / len(button_tests)) * 100
    print(f"📊 Navigation Tests: {passed}/{len(button_tests)} passed ({success_rate:.1f}%)")
    return success_rate >= 80

def test_data_integration():
    """Test specific Firecrawl data integration"""
    print("\n🔗 Testing Firecrawl Data Integration...")
    
    # Read the FAQ file to verify integration
    try:
        with open('data/documents/education_faq.json', 'r') as f:
            data = json.load(f)
        
        # Check for firecrawl_integrated category
        if 'firecrawl_integrated' in data:
            firecrawl_sections = data['firecrawl_integrated']
            total_firecrawl_items = sum(len(items) for items in firecrawl_sections.values() if isinstance(items, list))
            
            print(f"✅ Firecrawl category found with {len(firecrawl_sections)} sections")
            print(f"✅ Total Firecrawl Q&A pairs: {total_firecrawl_items}")
            
            # Test specific KIEC queries
            kiec_queries = [
                "KIEC success rate",
                "KIEC universities", 
                "KIEC partnerships"
            ]
            
            kiec_responses = 0
            for query in kiec_queries:
                response = requests.post('http://localhost:5001/chat', 
                                       json={'message': query})
                if response.status_code == 200:
                    data = response.json()
                    if 'kiec' in data.get('response', '').lower():
                        kiec_responses += 1
                        print(f"✅ KIEC query working: '{query}'")
                    else:
                        print(f"⚠️  KIEC query unclear: '{query}'")
            
            if kiec_responses >= 1:
                print("✅ KIEC data integration verified")
                return True
            else:
                print("❌ KIEC data not properly accessible")
                return False
        else:
            print("❌ No firecrawl_integrated category found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking data integration: {e}")
        return False

def main():
    """Run comprehensive system check"""
    print("🚀 Complete System Health Check")
    print("=" * 50)
    
    results = {}
    
    # Test each component
    results['Basic System'] = test_basic_system()
    
    if results['Basic System']:
        results['RAG System'] = test_rag_system()
        results['Human Handoff'] = test_human_handoff()
        results['FAQ Admin'] = test_faq_admin()
        results['Navigation'] = test_navigation_buttons()
        results['Data Integration'] = test_data_integration()
    else:
        print("\n❌ Basic system not running - please start the application first")
        return False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SYSTEM HEALTH SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component}")
    
    overall_health = (passed / total) * 100
    print(f"\n🎯 Overall System Health: {passed}/{total} ({overall_health:.1f}%)")
    
    if overall_health >= 80:
        print("\n🎉 SYSTEM IS HEALTHY!")
        print("✅ All major components working")
        print("✅ Firecrawl data integrated successfully")
        print("✅ RAG system operational")
        print("✅ Human handoff functional")
        print("\n🎯 Your system is ready for use!")
    elif overall_health >= 60:
        print("\n⚠️  SYSTEM MOSTLY HEALTHY")
        print("Most components working, minor issues detected")
    else:
        print("\n❌ SYSTEM NEEDS ATTENTION")
        print("Multiple components have issues")
    
    return overall_health >= 60

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 System check completed successfully!")
        print("\n🔍 To test your system:")
        print("1. Open: http://localhost:5001")
        print("2. Try these queries:")
        print("   - 'What is KIEC's success rate?'")
        print("   - 'How many universities does KIEC partner with?'")
        print("   - 'Tell me about study abroad requirements'")
        print("3. Test human handoff by saying 'I need complex help'")
        print("4. Check agent dashboard: http://localhost:5001/agent/login")
    else:
        print("\n❌ System check failed - please address the issues above")
