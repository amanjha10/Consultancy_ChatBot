#!/usr/bin/env python3
"""
Debug login by adding detailed error logging to the authentication routes
"""

import sys
import os
import traceback

# Add the project directory to Python path
sys.path.insert(0, '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot')

def patch_auth_routes():
    """Temporarily patch auth routes to add detailed logging"""
    
    # Read the current auth_routes.py
    auth_routes_path = '/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot/human_handoff/auth_routes.py'
    
    with open(auth_routes_path, 'r') as f:
        content = f.read()
    
    # Find the login route exception handler and add logging
    original_except = """        except Exception as e:
            db.session.rollback()
            error_message = 'An error occurred during login. Please try again.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_message}), 500
            else:
                flash(error_message, 'error')
                return render_template('singup_login/singup.html')"""
    
    patched_except = """        except Exception as e:
            db.session.rollback()
            # Log the actual exception for debugging
            print(f"LOGIN ERROR: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            error_message = f'An error occurred during login: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'message': error_message}), 500
            else:
                flash(error_message, 'error')
                return render_template('singup_login/singup.html')"""
    
    if original_except in content:
        patched_content = content.replace(original_except, patched_except)
        
        # Create backup
        backup_path = auth_routes_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Write patched version
        with open(auth_routes_path, 'w') as f:
            f.write(patched_content)
        
        print("✓ Auth routes patched with detailed error logging")
        print(f"✓ Backup created at: {backup_path}")
        return True
    else:
        print("✗ Could not find the exception handler to patch")
        return False

def test_login_via_web_request():
    """Test login using actual web request simulation"""
    
    from app import app
    from human_handoff.models import db, Student
    
    with app.test_client() as client:
        print("=== TESTING LOGIN VIA WEB REQUEST ===")
        
        # Test 1: GET request to login page
        print("\n1. Testing GET request to signup/login page...")
        response = client.get('/auth/login')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Login page failed: {response.status_code}")
            print(response.data.decode())
        
        # Test 2: POST request with valid credentials
        print("\n2. Testing POST request with valid credentials...")
        login_data = {
            'email': 'demo@student.com',
            'password': 'demo123'
        }
        
        try:
            response = client.post('/auth/login', data=login_data, follow_redirects=False)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            if response.status_code == 302:
                print(f"✓ Login successful - redirecting to: {response.location}")
            elif response.status_code == 200:
                print("Login returned 200, checking for errors in response...")
                response_text = response.data.decode()
                if 'error' in response_text.lower() or 'An error occurred' in response_text:
                    print("✗ Login failed with error message")
                    # Extract error message if visible
                    lines = response_text.split('\n')
                    for line in lines:
                        if 'error' in line.lower() or 'An error occurred' in line:
                            print(f"Error line: {line.strip()}")
                else:
                    print("✓ Login appears successful")
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                print(response.data.decode()[:500])
            
        except Exception as e:
            print(f"✗ Exception during login test: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    print("Starting detailed login debugging...")
    
    # Step 1: Patch auth routes for detailed logging
    if patch_auth_routes():
        print("\nPlease test the login now through the web interface.")
        print("The detailed error will be displayed in the browser and printed to console.")
        print("\nAlternatively, running the web request test...")
        
        # Step 2: Test via simulated web request
        test_login_via_web_request()
    
    print("\n" + "="*50)
    print("INSTRUCTIONS:")
    print("1. Try logging in through the browser at http://localhost:5000")
    print("2. Check the terminal output for detailed error messages")
    print("3. The original auth_routes.py is backed up as auth_routes.py.backup")
    print("4. To restore, run: mv human_handoff/auth_routes.py.backup human_handoff/auth_routes.py")
    print("="*50)
