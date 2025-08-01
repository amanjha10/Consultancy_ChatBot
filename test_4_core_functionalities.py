#!/usr/bin/env python3
"""
Test Script for 4 Core Chatbot Functionalities
This script tests all four core functionalities in order of priority.
"""

import requests
import json
import time
from datetime import datetime

class ChatbotFunctionalityTester:
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.test_results = []
        
    def send_message(self, message, context=None):
        """Send a message to the chatbot and return the response"""
        payload = {'message': message}
        if context:
            payload['context'] = context
            
        try:
            response = requests.post(f'{self.base_url}/chat', 
                                   json=payload, 
                                   timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}

    def test_greeting_recognition(self):
        """Test basic greeting recognition (part of core functionality 1)"""
        print('\n🟢 Testing Greeting Recognition')
        print('-' * 40)
        
        test_cases = [
            'hello',
            'hi', 
            'hy',  # This was fixed in the conversation summary
            'good morning',
            'hey there'
        ]
        
        all_passed = True
        for greeting in test_cases:
            response = self.send_message(greeting)
            if 'error' not in response and response.get('type') == 'initial_options':
                print(f'✅ "{greeting}" -> Greeting recognized')
            else:
                print(f'❌ "{greeting}" -> Failed: {response}')
                all_passed = False
                
        self.test_results.append(('Greeting Recognition', all_passed))
        return all_passed

    def test_level_wise_navigation(self):
        """Test Core Functionality 1: Level-wise Button Navigation"""
        print('\n🟢 Testing Core Functionality 1: Level-wise Button Navigation')
        print('-' * 60)
        
        test_cases = [
            {
                'name': 'Choose Country Navigation',
                'message': 'Choose country',
                'expected_type': 'country_selection',
                'should_contain': ['United States', 'Canada', 'United Kingdom']
            },
            {
                'name': 'Country Selection',
                'message': 'United States',
                'expected_type': 'course_selection',
                'should_contain': ['MS Computer Science', 'MBA']
            },
            {
                'name': 'Requirements Menu',
                'message': 'requirements',
                'expected_type': 'requirements_selection',
                'should_contain': ['Visa Requirements', 'Language Requirements']
            },
            {
                'name': 'Back to Main Menu',
                'message': 'back to main menu',
                'expected_type': 'main_menu',
                'should_contain': ['Choose Country', 'Browse Programs']
            }
        ]
        
        all_passed = True
        for test in test_cases:
            response = self.send_message(test['message'])
            if 'error' in response:
                print(f'❌ {test["name"]}: Error - {response["error"]}')
                all_passed = False
                continue
                
            # Check response type
            if response.get('type') != test['expected_type']:
                print(f'❌ {test["name"]}: Wrong type. Expected {test["expected_type"]}, got {response.get("type")}')
                all_passed = False
                continue
                
            # Check suggestions contain expected items
            suggestions = response.get('suggestions', [])
            missing_items = []
            for item in test['should_contain']:
                if not any(item in str(suggestion) for suggestion in suggestions):
                    missing_items.append(item)
                    
            if missing_items:
                print(f'❌ {test["name"]}: Missing suggestions: {missing_items}')
                all_passed = False
            else:
                print(f'✅ {test["name"]}: Navigation working correctly')
                
        self.test_results.append(('Level-wise Button Navigation', all_passed))
        return all_passed

    def test_rag_system(self):
        """Test Core Functionality 2: RAG-based System"""
        print('\n🟢 Testing Core Functionality 2: RAG-based System')
        print('-' * 50)
        
        test_cases = [
            {
                'name': 'Visa Requirements Query',
                'message': 'What are student visa requirements?',
                'should_contain': ['passport', 'university', 'funds'],
                'expected_type': 'faq_response'
            },
            {
                'name': 'Scholarship Query',
                'message': 'Tell me about scholarships available',
                'should_contain': ['scholarship', 'Fulbright'],
                'expected_type': 'faq_response'
            },
            {
                'name': 'Study Abroad Cost Query',
                'message': 'How much does studying abroad cost?',
                'should_contain': ['cost', 'tuition'],
                'expected_type': 'faq_response'
            },
            {
                'name': 'Why Study Abroad Query',
                'message': 'Why should I study abroad?',
                'should_contain': ['career', 'growth'],
                'expected_type': 'faq_response'
            }
        ]
        
        all_passed = True
        for test in test_cases:
            response = self.send_message(test['message'])
            if 'error' in response:
                print(f'❌ {test["name"]}: Error - {response["error"]}')
                all_passed = False
                continue
                
            # Check response type
            if response.get('type') != test['expected_type']:
                print(f'❌ {test["name"]}: Wrong type. Expected {test["expected_type"]}, got {response.get("type")}')
                all_passed = False
                continue
                
            # Check response contains expected content
            response_text = response.get('response', '').lower()
            missing_content = []
            for keyword in test['should_contain']:
                if keyword.lower() not in response_text:
                    missing_content.append(keyword)
                    
            if missing_content:
                print(f'❌ {test["name"]}: Missing content: {missing_content}')
                print(f'   Response: {response.get("response", "")[:100]}...')
                all_passed = False
            else:
                print(f'✅ {test["name"]}: RAG response provided correctly')
                
        self.test_results.append(('RAG-based System', all_passed))
        return all_passed

    def test_semantic_understanding(self):
        """Test Core Functionality 3: Semantic Understanding"""
        print('\n🟢 Testing Core Functionality 3: Semantic Understanding')
        print('-' * 55)
        
        test_cases = [
            {
                'name': 'Technology Studies Query',
                'message': 'I want to pursue higher education in technology field',
                'expected_types': ['faq_response', 'general']
            },
            {
                'name': 'General Study Abroad Query',
                'message': 'I am interested in studying overseas for my masters',
                'expected_types': ['faq_response', 'general']
            },
            {
                'name': 'Career Goals Query',
                'message': 'What are good career options after international education?',
                'expected_types': ['faq_response', 'general']
            }
        ]
        
        all_passed = True
        for test in test_cases:
            response = self.send_message(test['message'])
            if 'error' in response:
                print(f'❌ {test["name"]}: Error - {response["error"]}')
                all_passed = False
                continue
                
            # Check if we got a meaningful response
            response_text = response.get('response', '')
            if len(response_text) < 20:
                print(f'❌ {test["name"]}: Response too short: {response_text}')
                all_passed = False
                continue
                
            # Check response type is appropriate
            response_type = response.get('type', '')
            if response_type in test['expected_types']:
                print(f'✅ {test["name"]}: Semantic understanding working (type: {response_type})')
            else:
                print(f'❌ {test["name"]}: Unexpected type: {response_type}')
                all_passed = False
                
        self.test_results.append(('Semantic Understanding', all_passed))
        return all_passed

    def test_human_handoff_escalation(self):
        """Test Core Functionality 4: Human Handoff Escalation"""
        print('\n🟢 Testing Core Functionality 4: Human Handoff Escalation')
        print('-' * 55)
        
        test_cases = [
            {
                'name': 'Nonsense Query',
                'message': 'xyzabc random nonsense query 12345',
                'should_escalate': True
            },
            {
                'name': 'Irrelevant Query',
                'message': 'What is the weather like on Mars today?',
                'should_escalate': True
            },
            {
                'name': 'Very Complex Query',
                'message': 'I need help with transferring quantum physics credits from Neptune University to Earth while maintaining my alien visa status',
                'should_escalate': True
            }
        ]
        
        all_passed = True
        for test in test_cases:
            response = self.send_message(test['message'])
            if 'error' in response:
                print(f'❌ {test["name"]}: Error - {response["error"]}')
                all_passed = False
                continue
                
            # Check if escalation happened when expected
            escalated = response.get('escalated', False)
            response_type = response.get('type', '')
            
            if test['should_escalate']:
                if escalated and response_type == 'human_handoff_initiated':
                    print(f'✅ {test["name"]}: Correctly escalated to human handoff')
                    
                    # Check session info
                    session_info = response.get('session_info', {})
                    if session_info.get('status') == 'escalated':
                        print(f'   Session properly escalated with ID: {session_info.get("session_id", "N/A")}')
                    else:
                        print(f'   ⚠️  Session info incomplete: {session_info}')
                        
                else:
                    print(f'❌ {test["name"]}: Failed to escalate (escalated: {escalated}, type: {response_type})')
                    all_passed = False
            else:
                if not escalated:
                    print(f'✅ {test["name"]}: Correctly handled without escalation')
                else:
                    print(f'❌ {test["name"]}: Unnecessarily escalated')
                    all_passed = False
                    
        self.test_results.append(('Human Handoff Escalation', all_passed))
        return all_passed

    def test_priority_order(self):
        """Test that functionalities work in the correct priority order"""
        print('\n🟢 Testing Priority Order of Core Functionalities')
        print('-' * 50)
        
        # Test that button navigation takes precedence over other systems
        button_response = self.send_message('Choose country')
        if button_response.get('type') != 'country_selection':
            print('❌ Button navigation should have highest priority')
            self.test_results.append(('Priority Order', False))
            return False
            
        # Test that RAG system works for knowledge queries
        rag_response = self.send_message('What are visa requirements?')
        if rag_response.get('type') != 'faq_response':
            print('❌ RAG system should handle knowledge queries')
            self.test_results.append(('Priority Order', False))
            return False
            
        print('✅ Priority order working correctly')
        self.test_results.append(('Priority Order', True))
        return True

    def run_all_tests(self):
        """Run all tests and provide a comprehensive report"""
        print('🧪 Testing 4 Core Chatbot Functionalities')
        print('=' * 60)
        print('Testing in order of priority:')
        print('1. Level-wise Button Navigation (Highest Priority)')
        print('2. RAG-based System (Second Priority)')  
        print('3. Semantic Understanding (Third Priority)')
        print('4. Human Handoff Escalation (Last Resort)')
        print('=' * 60)
        
        start_time = time.time()
        
        # Test in order of priority
        tests = [
            self.test_greeting_recognition,
            self.test_level_wise_navigation,
            self.test_rag_system,
            self.test_semantic_understanding,
            self.test_human_handoff_escalation,
            self.test_priority_order
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f'❌ Test {test_func.__name__} failed with error: {e}')
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final Report
        print('\n' + '=' * 60)
        print('🎯 FINAL TEST RESULTS')
        print('=' * 60)
        
        for test_name, passed in self.test_results:
            status = '✅ PASS' if passed else '❌ FAIL'
            print(f'{status} {test_name}')
            
        print(f'\n📊 Summary: {passed_tests}/{total_tests} tests passed')
        print(f'⏱️  Duration: {duration:.2f} seconds')
        
        if passed_tests == total_tests:
            print('\n🎉 ALL TESTS PASSED! The chatbot is working correctly.')
            print('\n✅ All 4 core functionalities are operational:')
            print('   1. ✅ Level-wise Button Navigation')
            print('   2. ✅ RAG-based System') 
            print('   3. ✅ Semantic Understanding')
            print('   4. ✅ Human Handoff Escalation')
            return True
        else:
            print(f'\n⚠️  {total_tests - passed_tests} tests failed. Review the issues above.')
            return False

if __name__ == '__main__':
    print(f'Starting tests at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    tester = ChatbotFunctionalityTester()
    success = tester.run_all_tests()
    
    if success:
        print('\n🚀 System is ready for production!')
    else:
        print('\n🔧 System needs fixes before deployment.')
