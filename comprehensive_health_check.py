#!/usr/bin/env python3
"""
Complete System Health Check
Verifies all components of the EduConsult ChatBot system are working correctly
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5002"

class SystemHealthChecker:
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        
    def log_result(self, component, status, message, details=None):
        """Log test result"""
        self.results[component] = {
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {component}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_main_application(self):
        """Test main chatbot application"""
        print("\n🤖 Testing Main ChatBot Application...")
        
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            if response.status_code == 200:
                if "EduConsult" in response.text and "ChatBot" in response.text:
                    self.log_result("Main Application", "PASS", "ChatBot homepage accessible and properly rendered")
                else:
                    self.log_result("Main Application", "FAIL", "Homepage accessible but content missing")
            else:
                self.log_result("Main Application", "FAIL", f"Homepage returned status {response.status_code}")
        except Exception as e:
            self.log_result("Main Application", "FAIL", f"Cannot access homepage: {str(e)}")
    
    def test_chat_functionality(self):
        """Test chat API endpoint"""
        print("\n💬 Testing Chat Functionality...")
        
        try:
            chat_data = {
                "message": "What is studying abroad?",
                "session_id": "health_check_session"
            }
            
            response = requests.post(f"{BASE_URL}/chat", 
                                   json=chat_data, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("response") and len(result["response"]) > 50:
                    self.log_result("Chat API", "PASS", "Chat responding with detailed answers")
                else:
                    self.log_result("Chat API", "FAIL", "Chat response too short or empty")
            else:
                self.log_result("Chat API", "FAIL", f"Chat API returned status {response.status_code}")
        except Exception as e:
            self.log_result("Chat API", "FAIL", f"Chat API error: {str(e)}")
    
    def test_agent_authentication(self):
        """Test agent authentication system"""
        print("\n🔐 Testing Agent Authentication...")
        
        try:
            # Test agent login page
            response = requests.get(f"{BASE_URL}/agent/login", timeout=10)
            if response.status_code == 200:
                self.log_result("Agent Login Page", "PASS", "Agent login page accessible")
                
                # Test first-time login detection
                if "first-time" in response.text.lower() or "create" in response.text.lower():
                    self.log_result("First-Time Login UI", "PASS", "First-time login interface available")
                else:
                    self.log_result("First-Time Login UI", "WARN", "First-time login UI may not be visible")
            else:
                self.log_result("Agent Login Page", "FAIL", f"Agent login page returned {response.status_code}")
        except Exception as e:
            self.log_result("Agent Authentication", "FAIL", f"Agent auth error: {str(e)}")
    
    def test_super_admin_system(self):
        """Test super admin functionality"""
        print("\n👑 Testing Super Admin System...")
        
        try:
            # Test super admin login page
            response = requests.get(f"{BASE_URL}/super-admin/login", timeout=10)
            if response.status_code == 200:
                self.log_result("Super Admin Login", "PASS", "Super admin login page accessible")
                
                # Test login functionality
                login_data = {"admin_id": "super_admin", "password": "admin123"}
                login_response = requests.post(f"{BASE_URL}/super-admin/login", 
                                             data=login_data, 
                                             timeout=10,
                                             allow_redirects=False)
                
                if login_response.status_code == 302:
                    self.log_result("Super Admin Auth", "PASS", "Super admin authentication working")
                else:
                    self.log_result("Super Admin Auth", "FAIL", "Super admin login failed")
            else:
                self.log_result("Super Admin Login", "FAIL", f"Super admin page returned {response.status_code}")
        except Exception as e:
            self.log_result("Super Admin System", "FAIL", f"Super admin error: {str(e)}")
    
    def test_human_handoff(self):
        """Test human handoff system"""
        print("\n🤝 Testing Human Handoff System...")
        
        try:
            # Test escalation endpoint
            escalation_data = {
                "message": "I need human help with my application",
                "session_id": "health_check_escalation"
            }
            
            response = requests.post(f"{BASE_URL}/escalate-to-human", 
                                   json=escalation_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("Human Handoff", "PASS", "Escalation system working")
                else:
                    self.log_result("Human Handoff", "FAIL", "Escalation failed")
            else:
                self.log_result("Human Handoff", "FAIL", f"Escalation endpoint returned {response.status_code}")
        except Exception as e:
            self.log_result("Human Handoff", "FAIL", f"Handoff error: {str(e)}")
    
    def test_rag_system(self):
        """Test RAG system functionality"""
        print("\n🧠 Testing RAG System...")
        
        try:
            # Test with a specific query that should trigger RAG
            rag_query = {
                "message": "What are the scholarship opportunities for international students?",
                "session_id": "health_check_rag"
            }
            
            response = requests.post(f"{BASE_URL}/chat", 
                                   json=rag_query,
                                   headers={"Content-Type": "application/json"},
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").lower()
                
                # Check if response contains scholarship-related information
                if any(keyword in response_text for keyword in ["scholarship", "financial aid", "funding", "grant"]):
                    self.log_result("RAG System", "PASS", "RAG system providing relevant information")
                else:
                    self.log_result("RAG System", "WARN", "RAG response may not be using knowledge base")
            else:
                self.log_result("RAG System", "FAIL", f"RAG query failed with status {response.status_code}")
        except Exception as e:
            self.log_result("RAG System", "FAIL", f"RAG error: {str(e)}")
    
    def test_realtime_features(self):
        """Test real-time features (SocketIO)"""
        print("\n⚡ Testing Real-time Features...")
        
        try:
            # Test SocketIO endpoint
            response = requests.get(f"{BASE_URL}/socket.io/?EIO=4&transport=polling", timeout=10)
            
            if response.status_code == 200:
                self.log_result("SocketIO", "PASS", "Real-time communication system active")
            else:
                self.log_result("SocketIO", "FAIL", f"SocketIO endpoint returned {response.status_code}")
        except Exception as e:
            self.log_result("SocketIO", "FAIL", f"Real-time features error: {str(e)}")
    
    def test_static_resources(self):
        """Test static resources"""
        print("\n📁 Testing Static Resources...")
        
        static_files = [
            "/static/style.css",
            "/static/script.js"
        ]
        
        for file_path in static_files:
            try:
                response = requests.get(f"{BASE_URL}{file_path}", timeout=10)
                if response.status_code == 200 or response.status_code == 304:
                    self.log_result(f"Static Resource {file_path}", "PASS", "File accessible")
                else:
                    self.log_result(f"Static Resource {file_path}", "FAIL", f"Status {response.status_code}")
            except Exception as e:
                self.log_result(f"Static Resource {file_path}", "FAIL", f"Error: {str(e)}")
    
    def test_database_health(self):
        """Test database connectivity through API"""
        print("\n🗄️ Testing Database Health...")
        
        try:
            # Test agent API that requires database
            response = requests.get(f"{BASE_URL}/agent/api/pending-sessions", timeout=10)
            
            # Expecting 401 (unauthorized) since we're not logged in, but this means DB is working
            if response.status_code == 401:
                self.log_result("Database Connectivity", "PASS", "Database accessible (authentication required)")
            elif response.status_code == 200:
                self.log_result("Database Connectivity", "PASS", "Database accessible and responding")
            else:
                self.log_result("Database Connectivity", "WARN", f"Unexpected database response: {response.status_code}")
        except Exception as e:
            self.log_result("Database Connectivity", "FAIL", f"Database error: {str(e)}")
    
    def run_comprehensive_check(self):
        """Run all system health checks"""
        print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target URL: {BASE_URL}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_main_application,
            self.test_chat_functionality,
            self.test_rag_system,
            self.test_agent_authentication,
            self.test_super_admin_system,
            self.test_human_handoff,
            self.test_realtime_features,
            self.test_static_resources,
            self.test_database_health
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate system health summary"""
        print("\n" + "=" * 60)
        print("📊 SYSTEM HEALTH SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        failed = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        warnings = sum(1 for r in self.results.values() if r['status'] == 'WARN')
        
        print(f"Total Components Tested: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        # Calculate health score
        health_score = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall System Health: {health_score:.1f}%")
        
        if health_score >= 90:
            status = "🟢 EXCELLENT"
            message = "System is running optimally!"
        elif health_score >= 75:
            status = "🟡 GOOD"
            message = "System is functioning well with minor issues"
        elif health_score >= 50:
            status = "🟠 FAIR"
            message = "System has some issues that need attention"
        else:
            status = "🔴 POOR"
            message = "System has significant issues requiring immediate attention"
        
        print(f"Status: {status}")
        print(f"Assessment: {message}")
        
        # List any failures
        if failed > 0:
            print(f"\n⚠️  Issues Requiring Attention:")
            for component, result in self.results.items():
                if result['status'] == 'FAIL':
                    print(f"   • {component}: {result['message']}")
        
        # List warnings
        if warnings > 0:
            print(f"\n💡 Minor Issues:")
            for component, result in self.results.items():
                if result['status'] == 'WARN':
                    print(f"   • {component}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        return health_score >= 75

if __name__ == "__main__":
    checker = SystemHealthChecker()
    is_healthy = checker.run_comprehensive_check()
    
    if is_healthy:
        print("🎉 System is healthy and ready for use!")
        sys.exit(0)
    else:
        print("🔧 System needs attention - check issues above")
        sys.exit(1)
