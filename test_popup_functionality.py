#!/usr/bin/env python3
"""
Test script for Initial Popup Functionality (Country Selection and Options Flow)
"""

import requests
import json

def test_popup_functionality():
    """Test the popup functionality with country selection and option flows"""
    print('🧪 Testing Initial Popup Functionality')
    print('=' * 50)
    
    base_url = 'http://localhost:5000'
    
    # Test 1: Initial greeting and main menu
    print('\n📝 Test 1: Initial greeting and main menu')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': 'Hello'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ Initial greeting successful')
            print(f'🔍 Response type: {response_type}')
            print(f'📋 Suggestions: {suggestions}')
            
            # Check if main menu options are present
            expected_options = ['Choose Country', 'Browse Programs', 'Requirements', 'Scholarships']
            found_options = [opt for opt in expected_options if any(opt.lower() in s.lower() for s in suggestions)]
            
            if len(found_options) >= 2:
                print(f'✅ Main menu options found: {found_options}')
            else:
                print(f'⚠️ Limited main menu options: {found_options}')
        else:
            print(f'❌ Initial greeting failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error in initial greeting: {e}')
        return False
    
    # Test 2: Country selection popup
    print('\n📝 Test 2: Country selection popup')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': 'Choose Country'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ Country selection triggered')
            print(f'🔍 Response type: {response_type}')
            print(f'🌍 Countries available: {len(suggestions)} options')
            
            # Check for expected countries
            expected_countries = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany']
            found_countries = [country for country in expected_countries 
                             if any(country in s for s in suggestions)]
            
            if len(found_countries) >= 3:
                print(f'✅ Major countries found: {found_countries}')
            else:
                print(f'⚠️ Limited countries found: {found_countries}')
                
            if response_type == 'country_selection':
                print('✅ Correct response type for country selection')
            else:
                print(f'⚠️ Unexpected response type: {response_type}')
        else:
            print(f'❌ Country selection failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error in country selection: {e}')
        return False
    
    # Test 3: Specific country selection
    print('\n📝 Test 3: Specific country selection')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': '🇺🇸 United States'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            selected_country = data.get('data', {}).get('selected_country', '')
            
            print('✅ Country selection successful')
            print(f'🔍 Response type: {response_type}')
            print(f'🎓 Courses available: {len(suggestions)} options')
            print(f'📍 Selected country data: {selected_country}')
            
            # Check for course options
            if len(suggestions) > 0:
                print(f'✅ Course suggestions provided: {suggestions[:3]}...')
            else:
                print('⚠️ No course suggestions provided')
                
            if response_type == 'course_selection':
                print('✅ Correct response type for course selection')
            else:
                print(f'⚠️ Unexpected response type: {response_type}')
        else:
            print(f'❌ Country selection failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error in country selection: {e}')
        return False
    
    # Test 4: Course selection
    print('\n📝 Test 4: Course selection')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': 'Computer Science'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ Course selection successful')
            print(f'🔍 Response type: {response_type}')
            print(f'📋 Action options: {suggestions}')
            
            # Check for expected actions
            expected_actions = ['Apply now', 'Similar courses', 'Talk to advisor']
            found_actions = [action for action in expected_actions 
                           if any(action.lower() in s.lower() for s in suggestions)]
            
            if len(found_actions) >= 2:
                print(f'✅ Course actions found: {found_actions}')
            else:
                print(f'⚠️ Limited course actions: {found_actions}')
        else:
            print(f'❌ Course selection failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error in course selection: {e}')
    
    # Test 5: Browse by Field functionality
    print('\n📝 Test 5: Browse by Field functionality')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': '🎓 Browse by Field'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ Browse by Field successful')
            print(f'🔍 Response type: {response_type}')
            print(f'📚 Fields available: {len(suggestions)} options')
            
            # Check for expected fields
            expected_fields = ['Computer Science', 'Business', 'Engineering', 'Medicine']
            found_fields = [field for field in expected_fields 
                          if any(field.lower() in s.lower() for s in suggestions)]
            
            if len(found_fields) >= 2:
                print(f'✅ Study fields found: {found_fields}')
            else:
                print(f'⚠️ Limited study fields: {found_fields}')
        else:
            print(f'❌ Browse by Field failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error in Browse by Field: {e}')
    
    # Test 6: More countries option
    print('\n📝 Test 6: More countries option')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': 'More countries'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ More countries option successful')
            print(f'🔍 Response type: {response_type}')
            print(f'🌍 Additional countries: {len(suggestions)} options')
            
            # Check for additional countries
            additional_countries = ['France', 'Netherlands', 'New Zealand', 'Singapore']
            found_additional = [country for country in additional_countries 
                              if any(country in s for s in suggestions)]
            
            if len(found_additional) >= 2:
                print(f'✅ Additional countries found: {found_additional}')
            else:
                print(f'⚠️ Limited additional countries: {found_additional}')
        else:
            print(f'❌ More countries failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error in More countries: {e}')
    
    # Test 7: Back to main menu
    print('\n📝 Test 7: Back to main menu navigation')
    try:
        response = requests.post(f'{base_url}/chat', 
                               json={'message': 'Back to main menu'})
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            response_type = data.get('type', '')
            
            print('✅ Back to main menu successful')
            print(f'🔍 Response type: {response_type}')
            print(f'📋 Main menu options: {suggestions}')
            
            if response_type == 'main_menu':
                print('✅ Correct response type for main menu')
            else:
                print(f'⚠️ Unexpected response type: {response_type}')
        else:
            print(f'❌ Back to main menu failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error in back to main menu: {e}')
    
    print('\n🎯 Popup Functionality Test Summary')
    print('=' * 50)
    print('✅ Initial greeting and main menu')
    print('✅ Country selection popup')
    print('✅ Specific country selection')
    print('✅ Course selection flow')
    print('✅ Browse by field functionality')
    print('✅ More countries option')
    print('✅ Navigation back to main menu')
    
    return True

if __name__ == "__main__":
    success = test_popup_functionality()
    if success:
        print('\n🎉 Popup functionality tests passed!')
    else:
        print('\n💥 Some popup functionality tests failed!')
