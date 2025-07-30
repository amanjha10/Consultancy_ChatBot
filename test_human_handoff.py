#!/usr/bin/env python3
"""
Test script for Human Handoff System
This script tests the basic functionality of the human handoff system
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestHumanHandoffSystem(unittest.TestCase):
    """Test cases for the human handoff system"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.secret_key = 'test-secret-key'
        
        # Initialize the human handoff system
        try:
            from human_handoff import init_database, db
            init_database(self.app)
            self.db = db
        except ImportError as e:
            self.skipTest(f"Human handoff system not available: {e}")
    
    def test_database_models(self):
        """Test database models can be imported and created"""
        try:
            from human_handoff.models import ChatSession, Message, Agent, AgentSession, SessionAnalytics
            
            with self.app.app_context():
                # Test creating a chat session
                session = ChatSession(session_id='test-session-123')
                self.assertEqual(session.session_id, 'test-session-123')
                self.assertFalse(session.requires_human)
                
                # Test creating an agent
                agent = Agent(
                    agent_id='test-agent',
                    name='Test Agent',
                    email='test@example.com',
                    specialization='Testing',
                    is_active=True,
                    status='available',
                    current_sessions=0,
                    max_concurrent_sessions=5
                )
                self.assertEqual(agent.agent_id, 'test-agent')
                self.assertTrue(agent.can_take_session())
                
                print("✅ Database models test passed")
        except ImportError as e:
            self.fail(f"Failed to import models: {e}")
    
    def test_session_manager(self):
        """Test session manager functionality"""
        try:
            from human_handoff.session_manager import SessionManager
            
            with self.app.app_context():
                manager = SessionManager()
                
                # Test fallback detection
                fallback_responses = [
                    "Sorry, I am unaware about this content",
                    "I'm not sure about that specific query",
                    "I apologize, but I'm not sure"
                ]
                
                for response in fallback_responses:
                    self.assertTrue(manager.detect_fallback(response))
                
                normal_response = "Here's information about studying abroad"
                self.assertFalse(manager.detect_fallback(normal_response))
                
                print("✅ Session manager test passed")
        except ImportError as e:
            self.fail(f"Failed to import session manager: {e}")
    
    def test_database_operations(self):
        """Test database operations"""
        try:
            from human_handoff.database import DatabaseManager
            from human_handoff.models import ChatSession, Agent
            
            with self.app.app_context():
                # Create tables
                self.db.create_all()
                
                # Test creating an agent
                agent = Agent(
                    agent_id='test-agent-db',
                    name='Test Agent DB',
                    email='testdb@example.com',
                    specialization='Database Testing'
                )
                self.db.session.add(agent)
                self.db.session.commit()
                
                # Test creating a session
                session = ChatSession(
                    session_id='test-session-db',
                    requires_human=True,
                    status='escalated'
                )
                self.db.session.add(session)
                self.db.session.commit()
                
                # Verify data was saved
                saved_agent = Agent.query.filter_by(agent_id='test-agent-db').first()
                self.assertIsNotNone(saved_agent)
                self.assertEqual(saved_agent.name, 'Test Agent DB')
                
                saved_session = ChatSession.query.filter_by(session_id='test-session-db').first()
                self.assertIsNotNone(saved_session)
                self.assertTrue(saved_session.requires_human)
                
                print("✅ Database operations test passed")
        except Exception as e:
            self.fail(f"Database operations test failed: {e}")
    
    def test_agent_routes_import(self):
        """Test that agent routes can be imported"""
        try:
            from human_handoff.agent_routes import agent_bp
            self.assertIsNotNone(agent_bp)
            print("✅ Agent routes import test passed")
        except ImportError as e:
            self.fail(f"Failed to import agent routes: {e}")
    
    def test_socketio_events_import(self):
        """Test that SocketIO events can be imported"""
        try:
            from human_handoff.socketio_events import init_socketio
            self.assertIsNotNone(init_socketio)
            print("✅ SocketIO events import test passed")
        except ImportError as e:
            self.fail(f"Failed to import SocketIO events: {e}")
    
    def test_config_import(self):
        """Test configuration import"""
        try:
            from human_handoff.config import HumanHandoffConfig, get_config
            
            config = HumanHandoffConfig()
            self.assertIsNotNone(config.DEFAULT_AGENTS)
            self.assertGreater(len(config.DEFAULT_AGENTS), 0)
            
            # Test getting config
            dev_config = get_config('development')
            self.assertIsNotNone(dev_config)
            
            print("✅ Configuration test passed")
        except ImportError as e:
            self.fail(f"Failed to import configuration: {e}")

def test_dependencies():
    """Test that all required dependencies are available"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_socketio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'human_handoff/__init__.py',
        'human_handoff/models.py',
        'human_handoff/database.py',
        'human_handoff/session_manager.py',
        'human_handoff/agent_routes.py',
        'human_handoff/socketio_events.py',
        'human_handoff/config.py',
        'templates/agent/login.html',
        'templates/agent/dashboard.html',
        'templates/agent/session_detail.html',
        'static/script.js',
        'static/style.css'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def run_integration_test():
    """Run a basic integration test"""
    print("\n🧪 Running integration test...")
    
    try:
        # Test Flask app creation
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.secret_key = 'test-secret'
        
        # Test human handoff initialization
        from human_handoff import init_database
        init_database(app)
        
        # Test agent blueprint registration
        from human_handoff.agent_routes import agent_bp
        app.register_blueprint(agent_bp)
        
        # Test SocketIO initialization
        from human_handoff.socketio_events import init_socketio
        socketio = init_socketio(app)
        
        print("✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Human Handoff System Test Suite")
    print("=" * 50)
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed")
        return False
    
    # Test file structure
    if not test_file_structure():
        print("\n❌ File structure test failed")
        return False
    
    # Run integration test
    if not run_integration_test():
        print("\n❌ Integration test failed")
        return False
    
    # Run unit tests
    print("\n🔬 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("1. Start the application: python app.py")
    print("2. Test user chat: http://localhost:5000")
    print("3. Test agent dashboard: http://localhost:5000/agent/login")
    print("4. Try escalation by asking: 'I need help with something complex'")
    
    return True

if __name__ == "__main__":
    main()
