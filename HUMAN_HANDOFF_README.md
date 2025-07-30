# EduConsult Human Handoff System

A comprehensive human handoff system that seamlessly escalates chatbot conversations to human agents when needed.

## 🌟 Features

### Core Functionality
- **Automatic Escalation**: Detects when the chatbot cannot provide adequate responses
- **Real-time Communication**: Uses WebSockets for instant messaging between users and agents
- **Session Management**: Tracks conversation history and context
- **Agent Dashboard**: Dedicated interface for human agents to manage conversations
- **Database Integration**: Stores all conversations, analytics, and agent data

### User Experience
- **Seamless Transition**: Users experience smooth handoff from bot to human
- **Real-time Notifications**: Instant updates when agents join or respond
- **Conversation History**: Complete chat history preserved during handoff
- **Status Indicators**: Clear indication when chatting with bot vs. human

### Agent Features
- **Dashboard Overview**: View pending and assigned sessions
- **Real-time Chat**: Instant messaging with users
- **Session Management**: Assign, complete, and transfer conversations
- **Analytics**: View session statistics and performance metrics

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd Consultancy_ChatBot

# Run the setup script
python setup_human_handoff.py
```

### 2. Configuration

Update the `.env` file with your configuration:

```env
# Required: Add your Gemini API key
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Customize other settings
SECRET_KEY=your-secret-key-change-this-in-production
MAX_CONCURRENT_SESSIONS_PER_AGENT=5
```

### 3. Start the Application

```bash
python app.py
```

### 4. Access the System

- **User Chat**: http://localhost:5000
- **Agent Dashboard**: http://localhost:5000/agent/login

## 👥 Default Agent Accounts

| Agent ID | Name | Specialization | Password |
|----------|------|----------------|----------|
| agent_001 | Sarah Johnson | General Counselor | any |
| agent_002 | Michael Chen | US Universities | any |
| agent_003 | Emma Williams | UK Universities | any |
| agent_004 | David Kumar | Technical Support | any |

*Note: For demo purposes, any password works. Implement proper authentication for production.*

## 🔧 How It Works

### 1. Escalation Triggers

The system automatically escalates conversations when:
- Bot provides fallback responses (e.g., "I'm not sure about that")
- User explicitly requests human help
- Multiple consecutive fallback responses occur

### 2. Real-time Flow

```
User Message → Bot Processing → Fallback Detected → Session Escalated → Agent Notified → Real-time Chat
```

### 3. Database Schema

- **chat_sessions**: Stores session information and status
- **messages**: All conversation messages with metadata
- **agents**: Human agent profiles and availability
- **agent_sessions**: Agent-session assignments
- **session_analytics**: Performance and usage statistics

## 📊 Agent Dashboard Guide

### Dashboard Overview
- **Pending Sessions**: Unassigned escalated conversations
- **My Sessions**: Currently assigned conversations
- **Statistics**: Performance metrics and session counts

### Managing Sessions
1. **Take Session**: Assign pending session to yourself
2. **Chat**: Real-time messaging with users
3. **Complete**: Mark session as resolved
4. **View History**: Review complete conversation

### Real-time Features
- Instant message delivery
- Typing indicators
- Connection status
- Auto-refresh pending sessions

## 🛠️ Technical Architecture

### Backend Components
- **Flask-SocketIO**: Real-time WebSocket communication
- **SQLAlchemy**: Database ORM and session management
- **Session Manager**: Conversation tracking and escalation logic
- **Agent Routes**: REST API for agent operations

### Frontend Components
- **Socket.IO Client**: Real-time messaging
- **Agent Dashboard**: Vue-like reactive interface
- **User Chat**: Enhanced with real-time capabilities
- **Notification System**: Status updates and alerts

### Database Design
```sql
chat_sessions (session management)
├── messages (conversation history)
├── agents (human agent profiles)
├── agent_sessions (assignments)
└── session_analytics (metrics)
```

## 🔒 Security Considerations

### Development
- Simple agent authentication (any password)
- Local SQLite database
- Basic session management

### Production Recommendations
- Implement proper agent authentication
- Use PostgreSQL or similar database
- Add rate limiting and input validation
- Enable HTTPS and secure cookies
- Implement proper error handling

## 📈 Analytics & Monitoring

### Session Metrics
- Total messages per session
- Escalation time and reasons
- Resolution time
- Agent performance

### System Metrics
- Active sessions
- Agent availability
- Response times
- User satisfaction

## 🎨 Customization

### Adding New Agents
```python
# In human_handoff/config.py
DEFAULT_AGENTS.append({
    'agent_id': 'agent_005',
    'name': 'New Agent',
    'email': 'agent@company.com',
    'specialization': 'Custom Specialty'
})
```

### Customizing Escalation Triggers
```python
# In human_handoff/config.py
ESCALATION_TRIGGERS.extend([
    'custom trigger phrase',
    'another escalation keyword'
])
```

### UI Customization
- Modify CSS in `static/style.css`
- Update templates in `templates/agent/`
- Customize notifications in JavaScript

## 🐛 Troubleshooting

### Common Issues

**Database not initialized**
```bash
python -c "from human_handoff.models import init_database; from flask import Flask; app = Flask(__name__); app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///human_handoff.db'; init_database(app)"
```

**SocketIO connection issues**
- Check if port 5000 is available
- Verify firewall settings
- Ensure SocketIO client library is loaded

**Agent login problems**
- Verify agent exists in database
- Check agent status (should be active)
- Clear browser cache and cookies

### Debug Mode
Enable debug logging by setting:
```env
FLASK_ENV=development
SQLALCHEMY_ECHO=true
```

## 📝 API Reference

### REST Endpoints
- `GET /agent/api/pending-sessions` - Get pending sessions
- `GET /agent/api/my-sessions` - Get agent's sessions
- `POST /agent/api/session/{id}/assign` - Assign session
- `POST /agent/api/session/{id}/send-message` - Send message
- `POST /agent/api/session/{id}/complete` - Complete session

### SocketIO Events
- `join_session` - Join session room
- `send_message` - Send real-time message
- `agent_typing` - Typing indicator
- `session_escalated` - Escalation notification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the EduConsult chatbot system. Please refer to the main project license.

## 🆘 Support

For issues and questions:
1. Check this README
2. Review the troubleshooting section
3. Check the console for error messages
4. Create an issue with detailed information

---

**Happy Chatting! 🤖➡️👨‍💼**
