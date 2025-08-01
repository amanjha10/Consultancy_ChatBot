#!/usr/bin/env python3
"""
Browser Compatibility Test for EduConsult Chatbot
Tests the chat functionality to ensure it works across different browsers
"""

import requests
import json
import time
import sys

def test_basic_connectivity():
    """Test basic server connectivity"""
    print('🔌 Testing Basic Connectivity')
    print('-' * 40)
    
    try:
        response = requests.get('http://localhost:5001', timeout=10)
        if response.status_code == 200:
            print('✅ Server is running and accessible')
            print(f'   Response headers: {dict(response.headers)}')
            return True
        else:
            print(f'❌ Server returned status: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Cannot connect to server: {e}')
        return False

def test_static_files():
    """Test static file access"""
    print('\n📄 Testing Static File Access')
    print('-' * 40)
    
    static_files = [
        '/static/style.css',
        '/static/script.js'
    ]
    
    all_passed = True
    for file_path in static_files:
        try:
            response = requests.get(f'http://localhost:5001{file_path}', timeout=5)
            if response.status_code == 200:
                print(f'✅ {file_path} - accessible')
            else:
                print(f'❌ {file_path} - status {response.status_code}')
                all_passed = False
        except Exception as e:
            print(f'❌ {file_path} - error: {e}')
            all_passed = False
    
    return all_passed

def test_socketio_endpoint():
    """Test SocketIO endpoint availability"""
    print('\n🔌 Testing SocketIO Endpoint')
    print('-' * 40)
    
    try:
        # Test polling transport (initial connection method)
        response = requests.get('http://localhost:5001/socket.io/?EIO=4&transport=polling', timeout=5)
        
        if response.status_code == 200 and response.text.startswith('0'):
            print('✅ SocketIO endpoint accessible')
            print(f'   Response: {response.text[:50]}...')
            return True
        else:
            print(f'❌ SocketIO endpoint returned: {response.status_code}')
            print(f'   Response: {response.text[:100]}')
            return False
    except Exception as e:
        print(f'❌ SocketIO endpoint error: {e}')
        return False

def test_chat_api():
    """Test the main chat API endpoint"""
    print('\n💬 Testing Chat API')
    print('-' * 40)
    
    test_messages = [
        "Hello",
        "United States",
        "Computer Science",
        "What are the requirements?"
    ]
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    all_passed = True
    
    for i, message in enumerate(test_messages, 1):
        try:
            payload = {
                'message': message,
                'context': {}
            }
            
            print(f'Test {i}: Sending "{message}"')
            
            response = session.post(
                'http://localhost:5001/chat',
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and data['response']:
                    print(f'✅ Received response: {data["response"][:100]}...')
                    
                    # Check for additional data
                    if 'suggestions' in data:
                        print(f'   📋 Suggestions: {len(data["suggestions"])} items')
                    if 'type' in data:
                        print(f'   🏷️  Response type: {data["type"]}')
                    
                else:
                    print(f'❌ Empty or invalid response: {data}')
                    all_passed = False
            else:
                print(f'❌ Chat API returned status: {response.status_code}')
                print(f'   Response: {response.text[:200]}')
                all_passed = False
                
        except Exception as e:
            print(f'❌ Chat API error: {e}')
            all_passed = False
        
        # Small delay between requests
        time.sleep(1)
    
    return all_passed

def test_cors_headers():
    """Test CORS headers for cross-origin compatibility"""
    print('\n🌐 Testing CORS Headers')
    print('-' * 40)
    
    try:
        # Test with different origins
        origins = [
            'http://localhost:3000',
            'http://127.0.0.1:8080',
            'https://example.com'
        ]
        
        for origin in origins:
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            # Test preflight request
            response = requests.options('http://localhost:5001/chat', headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                cors_headers = {k: v for k, v in response.headers.items() if k.startswith('Access-Control')}
                if cors_headers:
                    print(f'✅ CORS enabled for {origin}')
                    print(f'   Headers: {cors_headers}')
                else:
                    print(f'⚠️  No CORS headers for {origin}')
            else:
                print(f'⚠️  Preflight failed for {origin}: {response.status_code}')
        
        return True
        
    except Exception as e:
        print(f'❌ CORS test error: {e}')
        return False

def main():
    """Run all browser compatibility tests"""
    print('🧪 EduConsult Browser Compatibility Test')
    print('=' * 50)
    
    tests = [
        ('Basic Connectivity', test_basic_connectivity),
        ('Static Files', test_static_files),
        ('SocketIO Endpoint', test_socketio_endpoint),
        ('Chat API', test_chat_api),
        ('CORS Headers', test_cors_headers)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f'\n❌ {test_name} failed with error: {e}')
            results[test_name] = False
    
    # Summary
    print('\n' + '=' * 50)
    print('📊 TEST SUMMARY')
    print('=' * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{status} {test_name}')
    
    print(f'\nOverall: {passed}/{total} tests passed')
    
    if passed == total:
        print('\n🎉 All tests passed! The chatbot should work in external browsers.')
        print('\nTo test in external browsers:')
        print('1. Open Safari, Chrome, Firefox, or Brave')
        print('2. Navigate to: http://127.0.0.1:5001')
        print('3. Try sending messages to test functionality')
        return True
    else:
        print(f'\n⚠️  {total - passed} test(s) failed. Check the output above for details.')
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
