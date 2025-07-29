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
    'hello', 'hi', 'hey', 'how are you', 'good morning', 'good afternoon', 'good evening', 'greetings', 'what\'s up', 'how\'s it going', 'namaste'
]

def is_greeting_query(user_message):
    msg = user_message.lower().strip()
    return any(kw in msg for kw in GREETING_KEYWORDS)

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
    """Query RAG system for document-based answers and return best match and score"""
    results = RAG.search(user_input, k=3)
    if not results:
        return None, 0.0
    # Try to find a general advice chunk (e.g. 'why study abroad', 'which country is best', etc.)
    from difflib import SequenceMatcher
    best = None
    score = 0.0
    for res in results:
        s = SequenceMatcher(None, user_input.lower(), res['question'].lower()).ratio()
        if s > score:
            best = res
            score = s
    return best, score

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
    data = request.json
    user_message = data.get('message', '').strip()
    context = data.get('context', {})
    
    if not user_message:
        return jsonify({
            'response': "Please enter a message.",
            'suggestions': [],
            'type': 'text'
        })

    # 1. Try RAG system first for FAQ-style questions
    if RAG and RAG.is_initialized:
        try:
            rag_results = RAG.search(user_message, k=1)
            if rag_results and len(rag_results) > 0 and rag_results[0]['score'] > 0.7:
                result = rag_results[0]
                response = result['answer']
                
                # Add suggestions based on the question type
                suggestions = ['Choose country', 'Popular courses', 'Talk to advisor']
                if 'country' in result['question'].lower():
                    suggestions = COUNTRIES[:5] + ['Explore by field']
                elif 'course' in result['question'].lower():
                    suggestions = ['Popular courses', 'Browse by field', 'Talk to advisor']
                
                print(f"RAG match found with score {result['score']}")
                return jsonify({
                    'response': response,
                    'suggestions': suggestions,
                    'type': 'general_advice'
                })
        except Exception as e:
            print(f"Error in RAG search: {e}")
    
    # 2. Handle standard button responses and other cases
    # Handle greetings/conversational queries first
    if is_greeting_query(user_message):
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

    # Check for button selections
    if user_message in COUNTRIES:
        # Country selected
        country_courses = COURSES_DATABASE.get(user_message, [])
        course_names = [course['name'] for course in country_courses]
        
        response = f"Great choice! Here are popular courses in {user_message}:"
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
    elif user_message in FIELDS_OF_STUDY:
        # Find courses in this field
        matching_courses = []
        for courses in COURSES_DATABASE.values():
            for course in courses:
                if user_message.lower() in course['name'].lower():
                    matching_courses.append(course['name'])
        
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
    response = "I'm not sure about that specific query. Would you like to talk to our customer service officer for personalized assistance?<br><br><em>Is there anything else I can help you with?</em>"
    advisor = CUSTOMER_ADVISORS[3]  # General counselor
    return jsonify({
        'response': response,
        'suggestions': ['Yes, connect me', 'No, continue with bot', 'Start over'],
        'type': 'escalation_offer',
        'advisor': advisor
    })

@app.route('/admin/add-faq', methods=['GET', 'POST'])
def add_faq():
    success = None
    error = None
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        category = request.form.get('category', '').strip()  # New: get selected category
        if not question or not answer or not category:
            error = "Question, answer, and category are required."
        else:
            try:
                with open('data/documents/education_faq.json', 'r') as f:
                    faq_data = json.load(f)
                # Parse category (e.g., 'general_queries.study_abroad_basics')
                cat_parts = category.split('.')
                if len(cat_parts) == 2:
                    top, sub = cat_parts
                    if top in faq_data and sub in faq_data[top]:
                        faq_data[top][sub].append({
                            "question": question,
                            "answer": answer,
                            "section": "Custom FAQ",
                            "page": 0,
                            "document": "Admin Added FAQ",
                            "chunk_id": str(uuid.uuid4())
                        })
                    else:
                        error = f"Category '{category}' not found in FAQ database."
                        return render_template('add_faq.html', success=success, error=error)
                else:
                    error = "Invalid category format."
                    return render_template('add_faq.html', success=success, error=error)
                with open('data/documents/education_faq.json', 'w') as f:
                    json.dump(faq_data, f, indent=4)
                # Re-index RAG system
                rag = RAGSystem()
                rag.load_documents('data/documents/education_faq.json')
                rag.save('data/vectors')
                success = "FAQ added and indexed successfully!"
            except Exception as e:
                error = f"Error saving FAQ: {e}"
    return render_template('add_faq.html', success=success, error=error)

if __name__ == '__main__':
    app.run(debug=True)