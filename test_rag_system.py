#!/usr/bin/env python3
"""
Test script for RAG system functionality
"""

import requests
import json

def test_rag_system():
    """Test the RAG system with various queries"""
    print('🧪 Testing RAG System')
    print('=' * 40)
    
    base_url = 'http://localhost:5000'
    
    test_cases = [
        {
            'name': 'Basic study abroad query',
            'message': 'What are the requirements for studying abroad?'
        },
        {
            'name': 'Visa requirements query',
            'message': 'What are student visa requirements?'
        },
        {
            'name': 'Scholarship query',
            'message': 'What scholarships are available?'
        },
        {
            'name': 'Language requirements',
            'message': 'Do I need to know English to study abroad?'
        },
        {
            'name': 'Cost information',
            'message': 'How much does studying abroad cost?'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'\n📝 Test {i}: {test_case["name"]}')
        
        try:
            response = requests.post(f'{base_url}/chat', 
                                   json={'message': test_case['message']},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', 'No response')
                response_type = data.get('type', 'Unknown')
                
                print(f'✅ Status: {response.status_code}')
                print(f'🔍 Type: {response_type}')
                print(f'📄 Response: {response_text[:150]}...')
                
                results.append({
                    'test': test_case['name'],
                    'status': 'PASS',
                    'response_length': len(response_text),
                    'type': response_type
                })
            else:
                print(f'❌ Failed: {response.status_code}')
                results.append({
                    'test': test_case['name'],
                    'status': 'FAIL',
                    'error': f'HTTP {response.status_code}'
                })
                
        except Exception as e:
            print(f'❌ Error: {str(e)}')
            results.append({
                'test': test_case['name'],
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary
    print('\n🎯 RAG System Test Summary')
    print('=' * 40)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    total = len(results)
    
    print(f'Tests Passed: {passed}/{total}')
    
    for result in results:
        status_icon = '✅' if result['status'] == 'PASS' else '❌'
        print(f'{status_icon} {result["test"]}: {result["status"]}')
    
    return passed == total

if __name__ == "__main__":
    success = test_rag_system()
    if success:
        print('\n🎉 All RAG tests passed!')
    else:
        print('\n💥 Some RAG tests failed!')
