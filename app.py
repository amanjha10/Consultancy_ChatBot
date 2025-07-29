from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import re
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from setup_rag import RAGSystem
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
# Create the model
model = genai.GenerativeModel(model_name='gemini-pro')

# Initialize RAG system with proper error handling
def initialize_rag():
    global RAG
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            RAG = RAGSystem()
            # Ensure the documents directory exists
            doc_path = 'data/documents/education_faq.json'
            if not os.path.exists(doc_path):
                print(f"Warning: Document file not found at {doc_path}")
                return False
                
            success = RAG.load_documents(doc_path)
            if success:
                print("RAG system initialized successfully!")
                return True
            else:
                print("RAG system failed to load documents")
                
        except Exception as e:
            print(f"Error initializing RAG system (attempt {retry_count + 1}/{max_retries}): {e}")
            RAG = None
        
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying in 5 seconds...")
            import time
            time.sleep(5)
    
    return False

# Initialize RAG on startup
RAG = None
rag_initialized = initialize_rag()
if not rag_initialized:
    print("Warning: RAG system failed to initialize. Some features may be limited.")

# Mock database - In production, use a real database
COUNTRIES = [
    'United States', 'Canada', 'United Kingdom', 'Australia', 
    'Germany', 'France', 'Netherlands', 'New Zealand', 
    'Singapore', 'Ireland', 'Japan', 'South Korea', 'Other'
]

COURSES_DATABASE = {
    'United States': [
        {
            'name': 'MS Computer Science',
            'university': 'Stanford University',
            'fees': '$52,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in CS/IT, GRE 320+, TOEFL 100+',
            'intake': 'Fall, Spring',
            'ranking': '#2 Global CS Rankings'
        },
        {
            'name': 'MBA',
            'university': 'Harvard Business School',
            'fees': '$73,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s degree, GMAT 730+, Work experience 3+ years',
            'intake': 'Fall',
            'ranking': '#1 Global MBA Rankings'
        },
        {
            'name': 'MS Data Science',
            'university': 'MIT',
            'fees': '$58,000/year',
            'duration': '1.5 years',
            'eligibility': 'Bachelor\'s in STEM, GRE 315+, Python/R proficiency',
            'intake': 'Fall, Spring',
            'ranking': '#1 Global Engineering Rankings'
        }
    ],
    'Canada': [
        {
            'name': 'MS Engineering',
            'university': 'University of Toronto',
            'fees': 'CAD 47,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in Engineering, IELTS 7.0+',
            'intake': 'Fall, Winter, Summer',
            'ranking': '#1 in Canada'
        },
        {
            'name': 'MBA',
            'university': 'Rotman School of Management',
            'fees': 'CAD 65,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s degree, GMAT 650+, Work experience 2+ years',
            'intake': 'Fall',
            'ranking': '#1 MBA in Canada'
        },
        {
            'name': 'MS Computer Science',
            'university': 'UBC',
            'fees': 'CAD 42,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in CS, GRE 310+, IELTS 6.5+',
            'intake': 'Fall, Winter',
            'ranking': '#3 in Canada'
        }
    ],
    'United Kingdom': [
        {
            'name': 'MS Finance',
            'university': 'London School of Economics',
            'fees': '£35,000/year',
            'duration': '1 year',
            'eligibility': 'Bachelor\'s in Finance/Economics, IELTS 7.0+',
            'intake': 'September',
            'ranking': '#2 Global Economics'
        },
        {
            'name': 'MS AI & Machine Learning',
            'university': 'Imperial College London',
            'fees': '£38,000/year',
            'duration': '1 year',
            'eligibility': 'Bachelor\'s in CS/Math, Strong programming skills',
            'intake': 'October',
            'ranking': '#4 Global Engineering'
        },
        {
            'name': 'MBA',
            'university': 'Oxford Said Business School',
            'fees': '£67,000/year',
            'duration': '1 year',
            'eligibility': 'Bachelor\'s degree, GMAT 690+, Work experience 3+ years',
            'intake': 'September',
            'ranking': '#6 Global MBA'
        }
    ],
    'Australia': [
        {
            'name': 'MS Information Technology',
            'university': 'University of Melbourne',
            'fees': 'AUD 44,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s degree, IELTS 6.5+',
            'intake': 'February, July',
            'ranking': '#1 in Australia'
        },
        {
            'name': 'MS Business Analytics',
            'university': 'Australian National University',
            'fees': 'AUD 45,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in Business/Math, IELTS 6.5+',
            'intake': 'February, July',
            'ranking': '#2 in Australia'
        }
    ],
    'Germany': [
        {
            'name': 'MS Mechanical Engineering',
            'university': 'Technical University of Munich',
            'fees': '€3,000/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in Engineering, German B2 or IELTS 6.5+',
            'intake': 'Winter, Summer',
            'ranking': '#1 Engineering in Germany'
        },
        {
            'name': 'MS Computer Science',
            'university': 'RWTH Aachen',
            'fees': '€3,500/year',
            'duration': '2 years',
            'eligibility': 'Bachelor\'s in CS, German B2 or IELTS 6.5+',
            'intake': 'Winter, Summer',
            'ranking': '#2 CS in Germany'
        }
    ]
}

STUDY_LEVELS = ['Undergraduate', 'Masters', 'PhD', 'Diploma', 'Certificate']
FIELDS_OF_STUDY = [
    'Computer Science', 'Business Administration', 'Engineering', 
    'Data Science', 'Medicine', 'Law', 'Arts & Humanities', 
    'Social Sciences', 'Natural Sciences', 'Other'
]

CUSTOMER_ADVISORS = [
    {'name': 'Anjali Sharma', 'specialization': 'USA & Canada', 'phone': '+91-9876543210'},
    {'name': 'Rajesh Kumar', 'specialization': 'UK & Europe', 'phone': '+91-9876543211'},
    {'name': 'Priya Patel', 'specialization': 'Australia & New Zealand', 'phone': '+91-9876543212'},
    {'name': 'Amit Singh', 'specialization': 'General Counseling', 'phone': '+91-9876543213'}
]

# Add a set of greeting/conversational queries
GREETING_KEYWORDS = [
    'hello', 'hi', 'hey', 'how are you', 'good morning', 'good afternoon', 
    'good evening', 'greetings', "what's up", "how's it going", 'namaste'
]

def is_greeting_query(user_message):
    """Check if a message is a greeting, being more precise to avoid false positives"""
    msg = user_message.lower().strip()
    
    # Check if message exactly matches a greeting
    if msg in GREETING_KEYWORDS:
        return True
        
    # Check if message starts with a greeting
    for greeting in GREETING_KEYWORDS:
        if msg.startswith(greeting + ' '):
            return True
            
    return False

def get_semantic_response(user_input, context=None):
    """Use Gemini API for semantic understanding"""
    try:
        prompt = f"""
        You are an education consultancy chatbot. Analyze this user input and provide a structured response.
        
        User input: "{user_input}"
        Context: {context or "Initial conversation"}
        
        Available countries: {', '.join(COUNTRIES)}
        Available study levels: {', '.join(STUDY_LEVELS)}
        Available fields: {', '.join(FIELDS_OF_STUDY)}
        
        Based on the user input, determine:
        1. Intent (country_inquiry, course_inquiry, general_info, greeting, other)
        2. Extracted entities (countries, courses, study level mentioned)
        3. Suggested response type (country_suggestions, course_suggestions, specific_info, clarification_needed)
        4. Confidence level (high, medium, low)
        
        Respond in JSON format:
        {{
            "intent": "...",
            "entities": {{
                "countries": [],
                "courses": [],
                "study_level": "",
                "field_of_study": ""
            }},
            "response_type": "...",
            "confidence": "...",
            "suggested_reply": "..."
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            result = json.loads(response.text)
            return result
        except:
            # Fallback if JSON parsing fails
            return {
                "intent": "other",
                "entities": {},
                "response_type": "clarification_needed",
                "confidence": "low",
                "suggested_reply": "I'd be happy to help you with your study abroad plans. Could you please tell me which country you're interested in?"
            }
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            "intent": "other",
            "entities": {},
            "response_type": "clarification_needed",
            "confidence": "low",
            "suggested_reply": "I'd be happy to help you with your study abroad plans. Could you please tell me which country you're interested in?"
        }

def get_rag_response(user_input):
    """Query RAG system for document-based answers with improved matching"""
    if not RAG or not RAG.is_initialized:
        return None, 0.0
        
    try:
        # Clean up input
        user_input = user_input.strip().lower()
        
        # Get multiple results
        results = RAG.search(user_input, k=3)
        if not results:
            return None, 0.0
            
        # Use both semantic similarity and text matching
        best_result = None
        best_score = 0.0
        
        for res in results:
            # Get base score from RAG
            score = res['score']
            
            # Boost score if question contains exact matches
            query_words = set(user_input.split())
            question_words = set(res['question'].lower().split())
            word_overlap = len(query_words.intersection(question_words))
            
            if word_overlap > 0:
                overlap_bonus = 0.1 * (word_overlap / len(query_words))
                score += overlap_bonus
            
            if score > best_score:
                best_result = res
                best_score = score
                
        print(f"Best RAG match: Score={best_score}, Question={best_result['question'] if best_result else 'None'}")
        return best_result, best_score
        
    except Exception as e:
        print(f"Error in RAG response: {e}")
        return None, 0.0

def search_courses(query, country=None):
    """Search courses based on query and country"""
    results = []
    
    if country and country in COURSES_DATABASE:
        courses = COURSES_DATABASE[country]
    else:
        courses = []
        for country_courses in COURSES_DATABASE.values():
            courses.extend(country_courses)
    
    # Simple keyword matching - in production, use better search
    query_lower = query.lower()
    for course in courses:
        if (query_lower in course['name'].lower() or 
            query_lower in course['university'].lower() or
            any(keyword in course['name'].lower() for keyword in query_lower.split())):
            results.append(course)
    
    return results[:5]  # Return top 5 matches

@app.route('/')
def index():
    """Render the main chatbot page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not request.json or 'message' not in request.json:
        return jsonify({'error': 'Invalid request'}), 400
        
    user_message = request.json['message'].strip()
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    context = request.json.get('context', 'Initial conversation')

    try:
        # Try RAG system first (if initialized)
        if RAG and RAG.is_initialized:
            print(f"\nProcessing message with RAG: '{user_message}'")
            try:
                # Get RAG results
                rag_results = RAG.search(user_message, k=3)
                if rag_results and len(rag_results) > 0:
                    # Debug output
                    print("\nRAG Results:")
                    for idx, res in enumerate(rag_results):
                        print(f"Match {idx + 1}:")
                        print(f"  Question: {res['question']}")
                        print(f"  Score: {res['score']}")
                        print(f"  Category: {res.get('category', 'N/A')}")
                    
                    # Use top result if we got any matches
                    # (scoring threshold is already applied in RAG.search())
                    if rag_results:
                        top_result = rag_results[0]
                        print(f"Using RAG response with score: {top_result['score']}")
                        
                        # Prepare suggestions based on category
                        suggestions = get_suggestions_for_category(top_result.get('category', 'general'))
                        
                        return jsonify({
                            'response': top_result['answer'],
                            'suggestions': suggestions,
                            'type': 'faq_response'
                        })
            except Exception as e:
                print(f"Error getting RAG response: {e}")

        # Check for greetings if no good RAG match was found
        if is_greeting_query(user_message):
            # Get appropriate time-based greeting
            current_time = datetime.now().hour
            if current_time < 12:
                greeting = "Good morning!"
            elif current_time < 17:
                greeting = "Good afternoon!"
            else:
                greeting = "Good evening!"
            response = f"{greeting} I'm EduConsult, your study abroad assistant. How can I help you today?"
            return jsonify({
                'response': response,
                'suggestions': ['Choose country', 'Popular courses', 'Talk to advisor'],
                'type': 'initial_options'
            })

        # Handle special actions first
        if user_message.lower() == 'start over':
            return jsonify({
                'response': "Let's start fresh! How can I help you with your study abroad plans?",
                'suggestions': [
                    '🌍 Choose Country',
                    '🎓 Browse Programs',
                    '📚 Requirements',
                    '💰 Scholarships',
                    '🗣️ Talk to Advisor'
                ],
                'type': 'main_menu',
                'clear_chat': True  # Frontend will clear chat history
            })
        
        if user_message.lower() == 'no, continue with bot':
            return jsonify({
                'response': "I'm here to help! What would you like to know about studying abroad?",
                'suggestions': [
                    '🌍 Choose Country',
                    '🎓 Browse Programs',
                    '📚 Requirements',
                    '💰 Scholarships',
                    '🗣️ Talk to Advisor'
                ],
                'type': 'main_menu'
            })

        # Handle navigation buttons
        if user_message.lower() in ['explore countries', 'browse countries', 'choose country', '🌍 choose country']:
            return jsonify({
                'response': "Here are the top study destinations. Which country interests you?",
                'suggestions': [
                    '🇺🇸 United States',
                    '🇨🇦 Canada',
                    '🇬🇧 United Kingdom',
                    '🇦🇺 Australia',
                    '🇩🇪 Germany',
                    'More countries',
                    '🎓 Browse by Field'
                ],
                'type': 'country_selection'
            })
        elif user_message.lower() == 'more countries':
            return jsonify({
                'response': "Here are more study destinations to explore:",
                'suggestions': [
                    '🇫🇷 France',
                    '🇳🇱 Netherlands',
                    '🇳🇿 New Zealand',
                    '🇸🇬 Singapore',
                    '🇮🇪 Ireland',
                    '🇯🇵 Japan',
                    'Back to main countries',
                    '🎓 Browse by Field'
                ],
                'type': 'country_selection'
            })
        elif user_message.lower() == 'requirements':
            return jsonify({
                'response': "What type of requirements would you like to know about?",
                'suggestions': [
                    'Visa Requirements',
                    'Language Requirements',
                    'Academic Requirements',
                    'Financial Requirements',
                    'Back to main menu'
                ],
                'type': 'requirements_selection'
            })
        elif user_message.lower() == 'back to main menu':
            return jsonify({
                'response': "What would you like to know about studying abroad?",
                'suggestions': [
                    '🌍 Choose Country',
                    '🎓 Browse Programs',
                    '📚 Requirements',
                    '💰 Scholarships',
                    '🗣️ Talk to Advisor'
                ],
                'type': 'main_menu'
            })
        
        # Handle standard button responses and other cases
        # Check for button selections
        # Clean country name from emoji if present
        clean_message = re.sub(r'[^\w\s]', '', user_message).strip()
        
        if clean_message in COUNTRIES:
            # Country selected
            country = clean_message
            country_courses = COURSES_DATABASE.get(country, [])
            course_names = [course['name'] for course in country_courses]
            
            # Get country emoji
            country_emojis = {
                'United States': '🇺🇸',
                'Canada': '🇨🇦',
                'United Kingdom': '🇬🇧',
                'Australia': '🇦🇺',
                'Germany': '🇩🇪',
                'France': '🇫🇷',
                'Netherlands': '🇳🇱',
                'New Zealand': '🇳🇿',
                'Singapore': '🇸🇬',
                'Ireland': '🇮🇪',
                'Japan': '🇯🇵'
            }
            emoji = country_emojis.get(country, '🌍')
            
            response = f"{emoji} Great choice! Here are popular courses in {country}:"
            return jsonify({
                'response': response,
                'suggestions': course_names + ['Show all courses', 'Different country'],
                'type': 'course_selection',
                'data': {'selected_country': user_message}
            })
        elif user_message in [course['name'] for courses in COURSES_DATABASE.values() for course in courses]:
            # Course selected - find the course details
            for country, courses in COURSES_DATABASE.items():
                for course in courses:
                    if course['name'] == user_message:
                        response = f"""
                        **{course['name']}** at **{course['university']}**
                        
                        💰 **Fees:** {course['fees']}
                        ⏱️ **Duration:** {course['duration']}
                        📋 **Eligibility:** {course['eligibility']}
                        📅 **Intake:** {course['intake']}
                        ⭐ **Ranking:** {course['ranking']}
                        
                        Would you like more information about this course or explore other options?
                        """
                        return jsonify({
                            'response': response,
                            'suggestions': ['Apply now', 'Similar courses', 'Different country', 'Talk to advisor'],
                            'type': 'course_details'
                        })
        elif user_message in STUDY_LEVELS:
            response = f"Perfect! You're interested in {user_message} programs. Which country interests you the most?"
            return jsonify({
                'response': response,
                'suggestions': COUNTRIES,
                'type': 'country_selection'
            })
        elif user_message == '🎓 Browse by Field' or user_message == 'Browse by Field':
            return jsonify({
                'response': "Choose your preferred field of study:",
                'suggestions': [
                    '💻 Computer Science',
                    '📊 Business Administration',
                    '⚡ Engineering',
                    '📈 Data Science',
                    '⚕️ Medicine',
                    '⚖️ Law',
                    'More Fields',
                    '🔙 Back to Countries'
                ],
                'type': 'field_selection'
            })
        elif user_message in FIELDS_OF_STUDY or any(field.lower() in user_message.lower() for field in FIELDS_OF_STUDY):
            # Clean field name from emoji
            field = next((f for f in FIELDS_OF_STUDY if f.lower() in user_message.lower()), user_message)
            
            # Find courses in this field
            matching_courses = []
            for country, courses in COURSES_DATABASE.items():
                for course in courses:
                    if field.lower() in course['name'].lower():
                        matching_courses.append(f"{course['name']} ({country})")
            
            if matching_courses:
                response = f"Great! Here are some {user_message} programs:"
                return jsonify({
                    'response': response,
                    'suggestions': list(set(matching_courses))[:8] + ['Show all countries'],
                    'type': 'course_selection'
                })
            else:
                response = f"I found programs related to {user_message}. Which country would you prefer?"
                return jsonify({
                    'response': response,
                    'suggestions': COUNTRIES,
                    'type': 'country_selection'
                })
        elif user_message.lower() in ['talk to advisor', 'human agent', 'speak to counselor']:
            advisor = CUSTOMER_ADVISORS[0]  # Default advisor
            response = f"""
            I'll connect you with our expert counselor!
            <br><br>
            <strong>Assigned Advisor:</strong> {advisor['name']}<br>
            <strong>Phone:</strong> {advisor['phone']}<br>
            <strong>Specialization:</strong> {advisor['specialization']}<br>
            <br>
            Our advisor will contact you shortly, or you can call directly.<br><br>
            <em>Is there anything else I can help you with?</em>
            """
            return jsonify({
                'response': response,
                'suggestions': ['Schedule callback', 'Continue with bot'],
                'type': 'human_handoff',
                'advisor': advisor
            })
        # 2. Use semantic understanding for free text (Gemini)
        semantic_result = get_semantic_response(user_message, context)
        if semantic_result['confidence'] == 'high' or semantic_result['intent'] in ['greeting', 'general_info']:
            return jsonify({
                'response': semantic_result['suggested_reply'],
                'suggestions': ['Choose country'] + COUNTRIES[:5] + ['Explore by field'],
                'type': 'general'
            })
        # 3. Escalate to human agent if neither RAG nor LLM is confident
        advisor = CUSTOMER_ADVISORS[3]  # General counselor
        response = f"""I apologize, but I'm not sure about that specific query. Would you like to speak with {advisor['name']}, our {advisor['specialization']} expert?

Contact details:
📞 Phone: {advisor['phone']}
🔧 Expertise: {advisor['specialization']}

They can provide you with personalized assistance and detailed information."""
        
        return jsonify({
            'response': response,
            'suggestions': ['Yes, connect me', 'No, continue with bot', 'Start over'],
            'type': 'escalation_offer',
            'advisor': advisor
        })
    except Exception as e:
        return jsonify({
            'response': f"Sorry, I encountered an error while processing your request: {e}",
            'suggestions': [],
            'type': 'text'
        })

@app.route('/admin/add-faq', methods=['GET', 'POST'])
def add_faq():
    global RAG
    success = None
    error = None
    
    if request.method == 'POST':
        try:
            # Get form data
            question = request.form.get('question')
            answer = request.form.get('answer')
            section = request.form.get('section', 'Custom FAQ')
            
            # Load existing FAQs
            with open('data/documents/education_faq.json', 'r') as f:
                data = json.load(f)
            
            # Create new FAQ entry
            new_faq = {
                'question': question,
                'answer': answer,
                'section': section,
                'page': 0,
                'document': 'Admin Added FAQ',
                'chunk_id': str(uuid.uuid4())
            }
            
            # Add to general_queries.custom_entries list
            if 'general_queries' not in data:
                data['general_queries'] = {}
            if 'custom_entries' not in data['general_queries']:
                data['general_queries']['custom_entries'] = []
            
            data['general_queries']['custom_entries'].append(new_faq)
            
            # Save updated JSON
            with open('data/documents/education_faq.json', 'w') as f:
                json.dump(data, f, indent=4)
            
            # Update embeddings
            if RAG is None:
                RAG = RAGSystem()
            
            if RAG.update_documents('data/documents/education_faq.json'):
                success = "FAQ added and embeddings updated successfully!"
            else:
                error = "Failed to update embeddings for the new FAQ"
                
        except Exception as e:
            error = f"Error saving FAQ: {e}"
            
    return render_template('add_faq.html', success=success, error=error)

# Category-specific suggestion buttons
CATEGORY_SUGGESTIONS = {
    'scholarships': ['Browse scholarships', 'Eligibility check', 'Apply now', 'Talk to advisor'],
    'admissions': ['Requirements', 'Application process', 'Document checklist', 'Talk to advisor'],
    'courses': ['Popular courses', 'Course details', 'Compare courses', 'Talk to advisor'],
    'general': ['Choose country', 'Popular courses', 'Talk to advisor']
}

def get_suggestions_for_category(category):
    """Get relevant suggestion buttons based on response category"""
    return CATEGORY_SUGGESTIONS.get(category.lower(), CATEGORY_SUGGESTIONS['general'])

if __name__ == '__main__':
    app.run(debug=True)