class ChatBot {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        this.modal = document.getElementById('advisorModal');
        this.context = {};
        
        this.initializeEventListeners();
        this.scrollToBottom();
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
            
            // Show advisor modal if type is human_handoff
            if (data.type === 'human_handoff' && data.advisor) {
                this.showAdvisorModal(data.advisor);
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTyping();
            this.addMessage('Sorry, something went wrong. Please try again.', 'bot', 'error');
        }

        this.scrollToBottom();
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        // Handle markdown-like formatting
        const formattedText = this.formatMessage(text);
        messageText.innerHTML = formattedText;

        const timestamp = document.createElement('div');
        timestamp.className = 'message-time';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

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