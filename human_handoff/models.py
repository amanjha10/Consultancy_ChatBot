"""
Database models for the Human Handoff System
SQLAlchemy models for chat sessions, messages, and agent management
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid

db = SQLAlchemy()

class ChatSession(db.Model):
    """Model for chat sessions"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, closed, escalated
    requires_human = db.Column(db.Boolean, default=False)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'))
    escalation_reason = db.Column(db.Text)
    escalated_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    user_satisfaction_rating = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    # Relationships
    messages = db.relationship('Message', backref='session', lazy=True, cascade='all, delete-orphan')
    assigned_agent = db.relationship('Agent', backref='assigned_sessions')
    analytics = db.relationship('SessionAnalytics', backref='session', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'requires_human': self.requires_human,
            'assigned_agent_id': self.assigned_agent_id,
            'escalation_reason': self.escalation_reason,
            'escalated_at': self.escalated_at.isoformat() if self.escalated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'user_satisfaction_rating': self.user_satisfaction_rating,
            'notes': self.notes
        }

class Message(db.Model):
    """Model for chat messages"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # user, bot, agent
    sender_id = db.Column(db.String(100))
    message_content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_fallback = db.Column(db.Boolean, default=False)
    message_metadata = db.Column(db.Text)  # JSON string for additional data
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'message_content': self.message_content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_fallback': self.is_fallback,
            'metadata': json.loads(self.message_metadata) if self.message_metadata else None
        }

    def set_metadata(self, data):
        """Set metadata as JSON string"""
        self.message_metadata = json.dumps(data) if data else None

    def get_metadata(self):
        """Get metadata as Python object"""
        return json.loads(self.message_metadata) if self.message_metadata else None

class Agent(db.Model):
    """Model for human agents"""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100))
    status = db.Column(db.String(20), default='available')  # available, busy, offline
    max_concurrent_sessions = db.Column(db.Integer, default=5)
    current_sessions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    total_sessions_handled = db.Column(db.Integer, default=0)
    average_response_time = db.Column(db.Integer, default=0)  # in seconds
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    agent_sessions = db.relationship('AgentSession', backref='agent', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'specialization': self.specialization,
            'status': self.status,
            'max_concurrent_sessions': self.max_concurrent_sessions,
            'current_sessions': self.current_sessions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'total_sessions_handled': self.total_sessions_handled,
            'average_response_time': self.average_response_time,
            'is_active': self.is_active
        }
    
    def can_take_session(self):
        """Check if agent can take a new session"""
        return (self.is_active and 
                self.status == 'available' and 
                self.current_sessions < self.max_concurrent_sessions)

class AgentSession(db.Model):
    """Model for agent-session relationships"""
    __tablename__ = 'agent_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, completed, transferred
    assigned_by_super_admin = db.Column(db.Boolean, default=False)
    super_admin_id = db.Column(db.Integer, db.ForeignKey('super_admins.id'), nullable=True)
    
    __table_args__ = (db.UniqueConstraint('agent_id', 'session_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'assigned_by_super_admin': self.assigned_by_super_admin,
            'super_admin_id': self.super_admin_id
        }

class SessionAnalytics(db.Model):
    """Model for session analytics"""
    __tablename__ = 'session_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    total_messages = db.Column(db.Integer, default=0)
    bot_messages = db.Column(db.Integer, default=0)
    user_messages = db.Column(db.Integer, default=0)
    agent_messages = db.Column(db.Integer, default=0)
    session_duration = db.Column(db.Integer, default=0)  # in seconds
    escalation_time = db.Column(db.Integer, default=0)  # time to escalation in seconds
    resolution_time = db.Column(db.Integer, default=0)  # time to resolution in seconds
    fallback_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'total_messages': self.total_messages,
            'bot_messages': self.bot_messages,
            'user_messages': self.user_messages,
            'agent_messages': self.agent_messages,
            'session_duration': self.session_duration,
            'escalation_time': self.escalation_time,
            'resolution_time': self.resolution_time,
            'fallback_count': self.fallback_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_database(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Insert default agents if they don't exist
        default_agents = [
            {'agent_id': 'agent_001', 'name': 'Sarah Johnson', 'email': 'sarah.johnson@educonsult.com', 'specialization': 'General Counselor'},
            {'agent_id': 'agent_002', 'name': 'Michael Chen', 'email': 'michael.chen@educonsult.com', 'specialization': 'US Universities Specialist'},
            {'agent_id': 'agent_003', 'name': 'Emma Williams', 'email': 'emma.williams@educonsult.com', 'specialization': 'UK Universities Specialist'},
            {'agent_id': 'agent_004', 'name': 'David Kumar', 'email': 'david.kumar@educonsult.com', 'specialization': 'Technical Support'}
        ]
        
        for agent_data in default_agents:
            existing_agent = Agent.query.filter_by(agent_id=agent_data['agent_id']).first()
            if not existing_agent:
                agent = Agent(**agent_data)
                db.session.add(agent)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")

def get_or_create_session(session_id, user_id=None):
    """Get existing session or create new one"""
    session = ChatSession.query.filter_by(session_id=session_id).first()
    if not session:
        session = ChatSession(session_id=session_id, user_id=user_id)
        db.session.add(session)
        db.session.commit()
    return session

class SuperAdmin(db.Model):
    """Model for super administrators who manage agent assignments"""
    __tablename__ = 'super_admins'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    permissions = db.Column(db.Text)  # JSON string for permissions

    # Relationships
    assigned_sessions = db.relationship('AgentSession', backref='super_admin', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def can_assign_sessions(self):
        """Check if super admin can assign sessions"""
        return self.is_active

    def get_managed_agents(self):
        """Get list of agents this super admin can manage"""
        # For now, super admin can manage all agents
        return Agent.query.filter_by(is_active=True).all()

    def get_agent_workload_summary(self):
        """Get summary of agent workloads"""
        agents = self.get_managed_agents()
        summary = []

        for agent in agents:
            pending_count = ChatSession.query.filter_by(
                assigned_agent_id=agent.id,
                status='escalated'
            ).count()

            active_count = AgentSession.query.filter_by(
                agent_id=agent.id,
                status='active'
            ).count()

            summary.append({
                'agent_id': agent.agent_id,
                'agent_name': agent.name,
                'status': agent.status,
                'current_sessions': agent.current_sessions,
                'max_capacity': agent.max_concurrent_sessions,
                'pending_assignments': pending_count,
                'active_sessions': active_count,
                'specialization': agent.specialization,
                'last_active': agent.last_active.isoformat() if agent.last_active else None,
                'workload_percentage': round((agent.current_sessions / max(agent.max_concurrent_sessions, 1)) * 100, 1)
            })

        return summary
