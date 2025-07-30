class ChatBot {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        this.modal = document.getElementById('advisorModal');
        this.context = {};
        this.sessionId = null;
        this.isHumanTakeover = false;
        this.socket = null;

        this.initializeEventListeners();
        this.initializeSocket();
        this.scrollToBottom();

        // Periodic session room check for escalated sessions
        setInterval(() => {
            if (this.isHumanTakeover && this.sessionId && this.socket) {
                console.log('Ensuring session room connection...');
                this.socket.emit('join_session', {
                    session_id: this.sessionId,
                    user_type: 'user'
                });
            }
        }, 30000); // Check every 30 seconds
    }

    initializeEventListeners() {
        // Send message on button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());

        // Suggestion buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn') || 
                e.target.classList.contains('quick-action-btn')) {
                const text = e.target.getAttribute('data-text') || e.target.textContent.trim();
                this.sendMessage(text);
            }
        });

        // Modal handling
        document.querySelector('.close').addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        document.getElementById('continueChat').addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        document.getElementById('scheduleCallback').addEventListener('click', () => {
            this.scheduleCallback();
        });

        // Close modal on outside click
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });

        // Auto-resize input
        this.messageInput.addEventListener('input', (e) => {
            this.updateSendButtonState();
        });

        this.updateSendButtonState();
    }

    updateSendButtonState() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText;
        this.sendButton.style.opacity = hasText ? '1' : '0.6';
    }

    initializeSocket() {
        // Initialize Socket.IO connection if available
        if (typeof io !== 'undefined') {
            this.socket = io();

            this.socket.on('connect', () => {
                console.log('Connected to real-time chat');
                console.log('Socket ID:', this.socket.id);
                this.showConnectionStatus('Connected to real-time chat', 'success');
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from real-time chat');
                this.showConnectionStatus('Disconnected from real-time chat', 'error');
            });

            this.socket.on('new_message', (data) => {
                console.log('Received new_message event:', data);
                console.log('Current sessionId:', this.sessionId);

                if (data.sender_type === 'agent' && data.session_id === this.sessionId) {
                    console.log('Adding agent message to chat');
                    this.addMessage(data.message_content, 'agent', 'agent_message', {
                        sender_name: data.sender_name || 'Agent',
                        timestamp: data.timestamp
                    });
                } else {
                    console.log('Message not for this session or not from agent');
                }
            });

            this.socket.on('human_takeover', (data) => {
                if (data.session_id === this.sessionId) {
                    this.handleHumanTakeover(data);
                }
            });

            this.socket.on('session_escalated_notification', (data) => {
                if (data.session_id === this.sessionId) {
                    this.showEscalationNotification(data.message);
                }
            });

            this.socket.on('agent_assigned_notification', (data) => {
                if (data.session_id === this.sessionId) {
                    this.showAgentAssignedNotification(data);
                }
            });

            this.socket.on('session_completed_notification', (data) => {
                if (data.session_id === this.sessionId) {
                    this.showSessionCompletedNotification(data.message);
                }
            });

            this.socket.on('agent_typing_status', (data) => {
                this.handleAgentTyping(data.is_typing);
            });
        }
    }

    async sendMessage(text = null) {
        const message = text || this.messageInput.value.trim();
        
        if (!message) return;

        // Clear input if not using suggestion
        if (!text) {
            this.messageInput.value = '';
            this.updateSendButtonState();
        }

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping();

        try {
            // Send to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: this.context
                })
            });

            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            // Check if we should clear the chat
            if (data.clear_chat) {
                this.clearChat();
            }
            
            // Add bot response
            this.addMessage(data.response, 'bot', data.type);
            
            // Update context if provided
            if (data.context) {
                this.context = { ...this.context, ...data.context };
            }
            
            // Add suggestions if any
            if (data.suggestions && data.suggestions.length > 0) {
                this.addSuggestions(data.suggestions, data.type);
            }
            
            // Handle human handoff scenarios
            if (data.type === 'human_handoff' && data.advisor) {
                this.showAdvisorModal(data.advisor);
            } else if (data.type === 'human_handoff_initiated' && data.escalated) {
                this.handleEscalation(data);
            } else if (data.type === 'human_handling' && data.escalated) {
                // Session is being handled by human - don't show bot response
                // Just ensure we're connected to the session room
                this.isHumanTakeover = true;
                if (data.session_info && data.session_info.session_id) {
                    this.sessionId = data.session_info.session_id;
                    if (this.socket) {
                        this.socket.emit('join_session', {
                            session_id: this.sessionId,
                            user_type: 'user'
                        });
                    }
                }
                return; // Don't process further - no bot response to show
            }

            // Extract session information if provided
            if (data.session_info && data.session_info.session_id) {
                this.sessionId = data.session_info.session_id;
                console.log('Session escalated, joining room:', this.sessionId);

                // Join the session room for real-time updates
                if (this.socket) {
                    this.socket.emit('join_session', {
                        session_id: this.sessionId,
                        user_type: 'user'
                    });
                    console.log('Emitted join_session event');
                } else {
                    console.log('Socket not available for joining session');
                }
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTyping();
            this.addMessage('Sorry, something went wrong. Please try again.', 'bot', 'error');
        }

        this.scrollToBottom();
    }

    addMessage(text, sender, type = null, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';

        // Set avatar icon based on sender type
        if (sender === 'bot') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else if (sender === 'agent') {
            avatar.innerHTML = '<i class="fas fa-user-tie"></i>';
            messageDiv.classList.add('agent-message');
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';

        // Handle markdown-like formatting
        const formattedText = this.formatMessage(text);
        messageText.innerHTML = formattedText;

        const timestamp = document.createElement('div');
        timestamp.className = 'message-time';

        // Use provided timestamp or current time
        const timeStr = metadata.timestamp ?
            new Date(metadata.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
            new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        // Add sender name for agent messages
        if (sender === 'agent' && metadata.sender_name) {
            timestamp.textContent = `${timeStr} - ${metadata.sender_name}`;
        } else {
            timestamp.textContent = timeStr;
        }

        content.appendChild(messageText);
        content.appendChild(timestamp);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.messagesContainer.appendChild(messageDiv);
    }

    formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/💰/g, '<i class="fas fa-dollar-sign" style="color: #28a745;"></i>')
            .replace(/⏱️/g, '<i class="fas fa-clock" style="color: #667eea;"></i>')
            .replace(/📋/g, '<i class="fas fa-clipboard-list" style="color: #6c757d;"></i>')
            .replace(/📅/g, '<i class="fas fa-calendar" style="color: #fd7e14;"></i>')
            .replace(/⭐/g, '<i class="fas fa-star" style="color: #ffc107;"></i>')
            .replace(/📞/g, '<i class="fas fa-phone" style="color: #28a745;"></i>')
            .replace(/🎓/g, '<i class="fas fa-graduation-cap" style="color: #667eea;"></i>');
    }

    addSuggestions(suggestions) {
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container';

        const title = document.createElement('div');
        title.className = 'suggestions-title';
        title.textContent = 'Quick Options:';

        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'suggestions';

        suggestions.forEach((suggestion, index) => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.setAttribute('data-text', suggestion);
            btn.textContent = suggestion;
            
            // Add country flags
            btn.innerHTML = this.addCountryFlags(suggestion);
            
            suggestionsDiv.appendChild(btn);
        });

        suggestionsContainer.appendChild(title);
        suggestionsContainer.appendChild(suggestionsDiv);
        this.messagesContainer.appendChild(suggestionsContainer);
    }

    addCountryFlags(text) {
        const flagMap = {
            'United States': '🇺🇸 United States',
            'Canada': '🇨🇦 Canada',
            'United Kingdom': '🇬🇧 United Kingdom',
            'Australia': '🇦🇺 Australia',
            'Germany': '🇩🇪 Germany',
            'France': '🇫🇷 France',
            'Netherlands': '🇳🇱 Netherlands',
            'New Zealand': '🇳🇿 New Zealand',
            'Singapore': '🇸🇬 Singapore',
            'Ireland': '🇮🇪 Ireland',
            'Japan': '🇯🇵 Japan',
            'South Korea': '🇰🇷 South Korea'
        };
        
        return flagMap[text] || text;
    }

    handleSpecialResponse(data) {
        switch (data.type) {
            case 'human_handoff':
            case 'escalation_offer':
                if (data.response.includes('talk to our customer service officer') || 
                    data.response.includes('Assigned Advisor')) {
                    this.showAdvisorModal(data.advisor);
                }
                break;
            
            case 'course_details':
                // Could add special formatting for course details
                break;
            
            case 'search_results':
                // Could add special formatting for search results
                break;
        }
    }

    showAdvisorModal(advisor) {
        if (advisor) {
            document.getElementById('advisorName').textContent = advisor.name;
            document.getElementById('advisorSpecialization').textContent = advisor.specialization;
            document.getElementById('advisorPhone').textContent = `📞 ${advisor.phone}`;
        }
        this.modal.style.display = 'block';
    }

    scheduleCallback() {
        this.modal.style.display = 'none';
        this.addMessage('Great! I\'ve scheduled a callback for you. Our advisor will contact you within 2 hours during business hours (9 AM - 6 PM IST).', 'bot');
        
        const confirmationSuggestions = [
            'Continue exploring courses',
            'Ask another question',
            'Get university rankings'
        ];
        this.addSuggestions(confirmationSuggestions);
        this.scrollToBottom();
    }

    showTyping() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.style.display = 'none';
    }

    clearChat() {
        // Clear messages
        this.messagesContainer.innerHTML = '';
        
        // Reset context
        this.context = {};
        
        // Add welcome message
        this.addMessage('👋 Hello! I\'m your study abroad assistant. How can I help you today?', 'bot', 'greeting');
        
        // Add initial suggestions
        this.addSuggestions([
            '🌍 Choose Country',
            '🎓 Browse Programs',
            '📚 Requirements',
            '💰 Scholarships',
            '🗣️ Talk to Advisor'
        ], 'main_menu');
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    // New methods for human handoff system
    handleEscalation(data) {
        this.isHumanTakeover = true;
        this.showEscalationNotification('Your conversation has been escalated to a human agent. Please wait while we connect you.');

        // Ensure we're connected to SocketIO and joined the session room
        if (this.socket && this.sessionId) {
            console.log('Re-joining session room after escalation:', this.sessionId);
            this.socket.emit('join_session', {
                session_id: this.sessionId,
                user_type: 'user'
            });
        }
    }

    handleHumanTakeover(data) {
        this.isHumanTakeover = true;
        this.showHumanTakeoverNotification(data.agent_id);
    }

    showEscalationNotification(message) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'system-notification escalation';
        notificationDiv.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-user-tie"></i>
                <span>${message}</span>
            </div>
        `;
        this.messagesContainer.appendChild(notificationDiv);
        this.scrollToBottom();
    }

    showAgentAssignedNotification(data) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'system-notification agent-assigned';
        notificationDiv.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-user-check"></i>
                <span>Agent ${data.agent_name} has been assigned to help you.</span>
            </div>
        `;
        this.messagesContainer.appendChild(notificationDiv);
        this.scrollToBottom();
    }

    showHumanTakeoverNotification(agentId) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'system-notification human-takeover';
        notificationDiv.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-handshake"></i>
                <span>You're now chatting with a human agent.</span>
            </div>
        `;
        this.messagesContainer.appendChild(notificationDiv);
        this.scrollToBottom();
    }

    showSessionCompletedNotification(message) {
        const notificationDiv = document.createElement('div');
        notificationDiv.className = 'system-notification session-completed';
        notificationDiv.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        this.messagesContainer.appendChild(notificationDiv);
        this.scrollToBottom();
    }

    showConnectionStatus(message, type) {
        // Create or update connection status indicator
        let statusDiv = document.getElementById('connection-status');
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'connection-status';
            statusDiv.className = 'connection-status';
            document.querySelector('.chat-container').prepend(statusDiv);
        }

        statusDiv.className = `connection-status ${type}`;
        statusDiv.innerHTML = `<i class="fas fa-wifi"></i> ${message}`;

        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    }

    handleAgentTyping(isTyping) {
        if (isTyping) {
            this.typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div> Agent is typing...';
            this.typingIndicator.style.display = 'flex';
        } else {
            this.typingIndicator.style.display = 'none';
        }
        this.scrollToBottom();
    }
}

// Enhanced message formatting for better UX
class MessageFormatter {
    static formatCourseInfo(course) {
        return `
            <div class="course-details">
                <h4>${course.name}</h4>
                <div class="course-info">
                    <div class="info-item">
                        <i class="fas fa-university"></i>
                        <span>${course.university}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-dollar-sign"></i>
                        <span>${course.fees}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-clock"></i>
                        <span>${course.duration}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-calendar"></i>
                        <span>${course.intake}</span>
                    </div>
                </div>
                <div class="eligibility">
                    <strong>Eligibility:</strong> ${course.eligibility}
                </div>
            </div>
        `;
    }
}

// Utility functions
const utils = {
    // Debounce function for input handling
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format currency
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Validate email
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
};

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatBot = new ChatBot();
    
    // Add some welcome animations
    setTimeout(() => {
        document.querySelector('.container').style.opacity = '1';
    }, 100);
    
    // Preload common responses for better UX
    const commonQueries = [
        'Choose country',
        'Popular courses',
        'Talk to advisor'
    ];
    
    // Service worker registration for offline functionality (optional)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(err => {
            console.log('Service worker registration failed:', err);
        });
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh connection status or update UI if needed
        console.log('Page is now visible');
    }
});

// Error handling for uncaught errors
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    // Could send error reports to analytics service
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Back online');
    // Could show a notification or refresh data
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    // Could show offline indicator
});