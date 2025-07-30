#!/usr/bin/env python3
"""
Setup script for Human Handoff System
This script helps set up the human handoff system for the EduConsult chatbot
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🤖 EduConsult Human Handoff System Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "human_handoff",
        "templates/agent",
        "static",
        "instance"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file with default configuration"""
    print("\n⚙️  Creating environment configuration...")
    
    env_content = """# EduConsult Human Handoff System Configuration

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///human_handoff.db

# Gemini API Configuration (required for chatbot)
GEMINI_API_KEY=your-gemini-api-key-here

# Human Handoff Configuration
MAX_CONCURRENT_SESSIONS_PER_AGENT=5
AUTO_ESCALATE_AFTER_FALLBACKS=2
ENABLE_SESSION_ANALYTICS=true

# Real-time Communication
SOCKETIO_ASYNC_MODE=threading
SOCKETIO_CORS_ALLOWED_ORIGINS=*

# Security (for production)
REQUIRE_AGENT_AUTHENTICATION=true
AGENT_SESSION_TIMEOUT_HOURS=8

# Notifications (optional)
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_SLACK_NOTIFICATIONS=false

# Performance
MESSAGE_RATE_LIMIT=10
CHAT_HISTORY_LIMIT=100
REFRESH_INTERVAL_SECONDS=30
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
        print("⚠️  Please update the GEMINI_API_KEY in .env file")
    else:
        print("ℹ️  .env file already exists, skipping creation")

def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    
    try:
        # Import and initialize database
        from human_handoff.models import init_database
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///human_handoff.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        init_database(app)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import flask
        import flask_sqlalchemy
        import flask_socketio
        print("✅ All required packages imported successfully")
        
        # Test database connection
        from human_handoff.models import db
        print("✅ Database models loaded successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Update your GEMINI_API_KEY in the .env file")
    print("2. Start the application: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    print("4. Access agent dashboard: http://localhost:5000/agent/login")
    print("\n👥 Default Agent Credentials:")
    print("   - agent_001 (Sarah Johnson - General Counselor)")
    print("   - agent_002 (Michael Chen - US Universities)")
    print("   - agent_003 (Emma Williams - UK Universities)")
    print("   - agent_004 (David Kumar - Technical Support)")
    print("   Password: any password (for demo)")
    print("\n📚 Documentation:")
    print("   - Check README.md for detailed usage instructions")
    print("   - Visit /agent/dashboard after logging in as an agent")
    print("   - Test escalation by asking complex questions in the chatbot")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Initialize database
    if not initialize_database():
        print("\n⚠️  Database initialization failed, but setup can continue")
        print("   You can initialize the database later by running the app")
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Some tests failed, but setup is mostly complete")
        print("   Please check for missing dependencies")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
