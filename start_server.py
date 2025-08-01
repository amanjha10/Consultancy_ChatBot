#!/usr/bin/env python3
"""
Startup script that kills any existing process on port 5001 and starts the EduConsult server
"""

import os
import sys
import subprocess
import signal
import time

def kill_process_on_port(port):
    """Kill any process running on the specified port"""
    print(f"🔍 Checking for existing processes on port {port}...")
    
    try:
        # Find process using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔪 Killing process {pid} on port {port}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        # If still running, force kill
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # Process already dead
                    except ProcessLookupError:
                        print(f"  Process {pid} already terminated")
                    except Exception as e:
                        print(f"  Error killing process {pid}: {e}")
            print(f"✅ Cleared all processes on port {port}")
        else:
            print(f"✅ No processes found on port {port}")
            
    except FileNotFoundError:
        print("⚠️ lsof command not found, skipping port check")
    except Exception as e:
        print(f"⚠️ Error checking port {port}: {e}")

def fix_escalation_database():
    """Fix the escalation database issue on startup"""
    print("🔧 Fixing escalation database issues...")
    
    # Import the fix function
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from human_handoff import db
        from human_handoff.models import ChatSession
        from app import app
        
        with app.app_context():
            # Reset all escalated sessions
            escalated_sessions = ChatSession.query.filter_by(requires_human=True).all()
            
            if escalated_sessions:
                print(f"  Found {len(escalated_sessions)} escalated sessions to reset")
                for session in escalated_sessions:
                    session.requires_human = False
                    session.status = 'active'
                    session.assigned_agent_id = None
                    session.escalation_reason = None
                    session.escalated_at = None
                
                db.session.commit()
                print(f"  ✅ Reset {len(escalated_sessions)} escalated sessions")
            else:
                print("  ✅ No escalated sessions found")
                
    except Exception as e:
        print(f"  ⚠️ Error fixing database: {e}")

def start_server():
    """Start the Flask server"""
    print("🚀 Starting EduConsult server...")
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Activate virtual environment and start server
    venv_path = os.path.join("..", "..", "env", "bin", "activate")
    
    if os.path.exists(venv_path):
        # Use virtual environment
        cmd = f"source {venv_path} && python app.py"
    else:
        # Use system Python
        cmd = "python3 app.py"
    
    print(f"Running: {cmd}")
    
    # Start the server
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    print("🎯 EduConsult Server Startup")
    print("=" * 50)
    
    # Step 1: Kill any existing process on port 5001
    kill_process_on_port(5001)
    
    # Step 2: Wait a moment for processes to fully terminate
    time.sleep(2)
    
    # Step 3: Fix database escalation issues
    try:
        fix_escalation_database()
    except Exception as e:
        print(f"⚠️ Could not fix database (server may not be initialized yet): {e}")
    
    # Step 4: Start the server
    start_server()
