"""
Super Admin Routes for Managing Agent Assignments
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, timedelta
import json
from .models import db, SuperAdmin, Agent, ChatSession, AgentSession, Message
from .socketio_events import get_socketio

super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

def super_admin_required(f):
    """Decorator to require super admin authentication"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'super_admin_id' not in session:
            return redirect(url_for('super_admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@super_admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Super admin login"""
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        password = request.form.get('password')
        
        # For demo purposes, simple authentication
        # In production, use proper password hashing
        if admin_id == 'super_admin' and password == 'admin123':
            # Get or create super admin
            super_admin = SuperAdmin.query.filter_by(admin_id=admin_id).first()
            if not super_admin:
                super_admin = SuperAdmin(
                    admin_id=admin_id,
                    name='Super Administrator',
                    email='admin@educonsult.com',
                    password_hash='hashed_password',  # In production, hash this
                    is_active=True
                )
                db.session.add(super_admin)
                db.session.commit()
            
            # Update last login
            super_admin.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session['super_admin_id'] = super_admin.id
            session['super_admin_name'] = super_admin.name
            
            return redirect(url_for('super_admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('super_admin/login.html')

@super_admin_bp.route('/logout')
def logout():
    """Super admin logout"""
    session.pop('super_admin_id', None)
    session.pop('super_admin_name', None)
    return redirect(url_for('super_admin.login'))

@super_admin_bp.route('/dashboard')
@super_admin_required
def dashboard():
    """Super admin dashboard"""
    super_admin = SuperAdmin.query.get(session['super_admin_id'])
    
    # Get pending sessions that need assignment
    pending_sessions = ChatSession.query.filter_by(
        requires_human=True,
        status='escalated',
        assigned_agent_id=None
    ).order_by(ChatSession.escalated_at.desc()).all()
    
    # Get agent workload summary
    agent_summary = super_admin.get_agent_workload_summary()
    
    # Get recent assignments made by this super admin
    recent_assignments = AgentSession.query.filter_by(
        super_admin_id=super_admin.id,
        assigned_by_super_admin=True
    ).order_by(AgentSession.assigned_at.desc()).limit(10).all()
    
    return render_template('super_admin/dashboard.html',
                         super_admin=super_admin,
                         pending_sessions=pending_sessions,
                         agent_summary=agent_summary,
                         recent_assignments=recent_assignments)

@super_admin_bp.route('/api/pending-sessions')
@super_admin_required
def api_pending_sessions():
    """API endpoint for pending sessions"""
    try:
        sessions = ChatSession.query.filter_by(
            requires_human=True,
            status='escalated',
            assigned_agent_id=None
        ).order_by(ChatSession.escalated_at.desc()).all()
        
        session_data = []
        for session in sessions:
            # Get latest message
            latest_message = Message.query.filter_by(
                session_id=session.session_id
            ).order_by(Message.timestamp.desc()).first()
            
            # Calculate priority and complexity
            priority = calculate_session_priority(session)
            complexity = estimate_session_complexity(session)
            
            session_data.append({
                'session_id': session.session_id,
                'escalated_at': session.escalated_at.isoformat() if session.escalated_at else None,
                'escalation_reason': session.escalation_reason,
                'priority': priority,
                'estimated_complexity': complexity,
                'latest_message': latest_message.message_content[:100] + '...' if latest_message and latest_message.message_content else 'No messages',
                'message_count': Message.query.filter_by(session_id=session.session_id).count(),
                'waiting_time': str(datetime.utcnow() - session.escalated_at) if session.escalated_at else 'Unknown'
            })
        
        return jsonify({'sessions': session_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@super_admin_bp.route('/api/agents')
@super_admin_required
def api_agents():
    """API endpoint for agent information"""
    try:
        super_admin = SuperAdmin.query.get(session['super_admin_id'])
        agent_summary = super_admin.get_agent_workload_summary()
        
        return jsonify({'agents': agent_summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@super_admin_bp.route('/api/assign-session', methods=['POST'])
@super_admin_required
def api_assign_session():
    """API endpoint to assign session to agent"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        agent_id = data.get('agent_id')
        
        if not session_id or not agent_id:
            return jsonify({'error': 'Session ID and Agent ID are required'}), 400
        
        # Get session and agent
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        
        if not chat_session:
            return jsonify({'error': 'Session not found'}), 404
        
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        if chat_session.assigned_agent_id:
            return jsonify({'error': 'Session already assigned'}), 400
        
        if not agent.can_take_session():
            return jsonify({'error': f'Agent {agent.name} cannot take more sessions'}), 400
        
        # Assign session
        chat_session.assigned_agent_id = agent.id
        chat_session.status = 'assigned'
        chat_session.updated_at = datetime.utcnow()
        
        # Update agent
        agent.current_sessions += 1
        agent.last_active = datetime.utcnow()
        
        # Create agent session record
        agent_session = AgentSession(
            agent_id=agent.id,
            session_id=session_id,
            assigned_by_super_admin=True,
            super_admin_id=session['super_admin_id']
        )
        
        db.session.add(agent_session)
        db.session.commit()
        
        # Send real-time notification to agent
        try:
            socketio = get_socketio()
            if socketio:
                notification_data = {
                    'session_id': session_id,
                    'assigned_by': 'Super Admin',
                    'assigned_at': datetime.utcnow().isoformat(),
                    'escalation_reason': chat_session.escalation_reason,
                    'priority': 'high'  # Super admin assignments are high priority
                }
                
                # Send to specific agent
                socketio.emit('session_assigned_by_super_admin', notification_data, room=f'agent_{agent.agent_id}')
                
                # Send to all agents for dashboard updates
                socketio.emit('session_assigned', {
                    'session_id': session_id,
                    'agent_id': agent.agent_id,
                    'agent_name': agent.name,
                    'assigned_by_super_admin': True
                }, room='agents')
                
                print(f"📢 Super admin assigned session {session_id} to {agent.name}")
        except Exception as e:
            print(f"Failed to send assignment notification: {e}")
        
        return jsonify({
            'message': f'Session assigned to {agent.name} successfully',
            'agent_name': agent.name,
            'session_id': session_id,
            'assigned_by_super_admin': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@super_admin_bp.route('/api/agent-details/<agent_id>')
@super_admin_required
def api_agent_details(agent_id):
    """Get detailed information about an agent"""
    try:
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Get agent's current sessions
        current_sessions = AgentSession.query.filter_by(
            agent_id=agent.id,
            status='active'
        ).all()
        
        session_details = []
        for agent_session in current_sessions:
            chat_session = ChatSession.query.filter_by(
                session_id=agent_session.session_id
            ).first()
            
            if chat_session:
                session_details.append({
                    'session_id': chat_session.session_id,
                    'escalated_at': chat_session.escalated_at.isoformat() if chat_session.escalated_at else None,
                    'escalation_reason': chat_session.escalation_reason,
                    'assigned_at': agent_session.assigned_at.isoformat() if agent_session.assigned_at else None,
                    'assigned_by_super_admin': agent_session.assigned_by_super_admin
                })
        
        return jsonify({
            'agent': agent.to_dict(),
            'current_sessions': session_details,
            'session_count': len(session_details)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_session_priority(session):
    """Calculate session priority (1-5, 5 being highest)"""
    priority = 1
    
    if session.escalated_at:
        # Higher priority for longer waiting sessions
        waiting_time = datetime.utcnow() - session.escalated_at
        if waiting_time > timedelta(hours=2):
            priority += 2
        elif waiting_time > timedelta(hours=1):
            priority += 1
    
    # Check for urgent keywords
    if session.escalation_reason:
        urgent_keywords = ['urgent', 'emergency', 'immediate', 'asap', 'critical']
        if any(keyword in session.escalation_reason.lower() for keyword in urgent_keywords):
            priority += 2
    
    return min(priority, 5)

def estimate_session_complexity(session):
    """Estimate session complexity"""
    message_count = Message.query.filter_by(session_id=session.session_id).count()
    
    if message_count > 10:
        return 'High'
    elif message_count > 5:
        return 'Medium'
    else:
        return 'Low'
