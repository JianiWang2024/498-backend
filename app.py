# backend APIs
# This file contains the Flask application for the FAQ API.
# It includes endpoints to get, add, update, and delete FAQs.
# Updated for PostgreSQL deployment on Railway

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import session
from config import Config
from models import db, FAQ, Log, Feedback, User, ConversationSession
from ai_service import ai_service
from keyword_service import keyword_service
from conversation_service import conversation_service

from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import timedelta, datetime
import os
import logging

# Configure logging for Railway deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration first
app.config.from_object(Config)

# Ensure SECRET_KEY is set for sessions
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    logger.warning("Using default SECRET_KEY - set SECRET_KEY environment variable in production")

# Temporary OpenAI API key for testing (remove in production)
if not app.config.get('OPENAI_API_KEY'):
    app.config['OPENAI_API_KEY'] = 'sk-4TMyDTGXFc6xoMQiWhkkAUgoPLJqWoAZUSpNGhdPdUftcFiF'
    logger.warning("Using temporary OpenAI API key - set OPENAI_API_KEY environment variable in production")

# Configure CORS to allow frontend access
CORS(app, 
     supports_credentials=True,
     origins=[
         "http://localhost:3000",  # 本地开发
         "https://498-frontend.vercel.app",  # Vercel前端
         "https://498-frontend-production.up.railway.app",  # Vercel部署的前端
         "https://*.vercel.app",   # 所有Vercel应用
         "https://*.railway.app",  # Railway应用
         "https://*.netlify.app",  # Netlify部署
         "https://*.github.io"     # GitHub Pages
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# initialize the database
db.init_app(app)

# Add health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server status"""
    try:
        # Check database connection
        db_status = check_db_connection()
        
        # Check environment variables
        env_status = {
            'SECRET_KEY': bool(app.config.get('SECRET_KEY')),
            'DATABASE_URL': bool(app.config.get('DATABASE_URL')),
            'RAILWAY_DEPLOYMENT': bool(app.config.get('RAILWAY_DEPLOYMENT'))
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if db_status else 'disconnected',
            'environment': env_status
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Add error handling middleware
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'Server error occurred'}), 500

# Add simple test endpoints for debugging
@app.route('/api/test/simple', methods=['GET'])
def test_simple():
    """Simple test endpoint to verify basic functionality"""
    return jsonify({'message': 'Simple test successful', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/test/db', methods=['GET'])
def test_db():
    """Test database operations"""
    try:
        # Test basic database operations
        faq_count = FAQ.query.count()
        user_count = User.query.count()
        
        return jsonify({
            'message': 'Database test successful',
            'faq_count': faq_count,
            'user_count': user_count,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return jsonify({
            'message': 'Database test failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test/session', methods=['GET'])
def test_session():
    """Test session functionality"""
    try:
        # Test session operations
        session['test_key'] = 'test_value'
        test_value = session.get('test_key')
        session.pop('test_key', None)
        
        return jsonify({
            'message': 'Session test successful',
            'test_value': test_value,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Session test failed: {e}")
        return jsonify({
            'message': 'Session test failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Add simple chat API for testing (without AI dependencies)
@app.route('/api/chat/simple', methods=['POST'])
def simple_chat():
    """Simple chat API without AI dependencies for testing"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Simple keyword-based response (no AI)
        user_question_lower = user_question.lower()
        
        if 'hello' in user_question_lower or 'hi' in user_question_lower:
            answer = "Hello! How can I help you today?"
        elif 'help' in user_question_lower:
            answer = "I'm here to help! What would you like to know?"
        elif 'faq' in user_question_lower:
            answer = "You can ask me any questions about our services."
        else:
            answer = "Thank you for your question. I'll get back to you soon."
        
        return jsonify({
            'question': user_question,
            'answer': answer,
            'source': 'simple_chat',
            'confidence': 'medium',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Simple chat API error: {e}")
        return jsonify({
            'question': user_question,
            'answer': 'Sorry, there was an error processing your request.',
            'source': 'error',
            'confidence': 'low',
            'error': str(e)
        }), 500

# Add hybrid FAQ search API (database first, then AI fallback)
@app.route('/api/faq/search', methods=['POST'])
def search_faq():
    """Hybrid FAQ search API: database first, then AI fallback"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get all FAQs from database
        all_faqs = FAQ.query.all()
        
        if not all_faqs:
            return jsonify({
                'question': user_question,
                'answer': 'No FAQs available in the database.',
                'source': 'database',
                'confidence': 'low',
                'found': False
            }), 200
        
        # Simple keyword matching (case-insensitive)
        user_question_lower = user_question.lower()
        best_match = None
        best_score = 0
        
        for faq in all_faqs:
            question_lower = faq.question.lower()
            answer_lower = faq.answer.lower()
            
            # Calculate simple relevance score
            score = 0
            
            # Check if user question contains FAQ question keywords
            question_words = question_lower.split()
            for word in question_words:
                if len(word) > 2 and word in user_question_lower:
                    score += 1
            
            # Check if user question contains FAQ answer keywords
            answer_words = answer_lower.split()
            for word in answer_words:
                if len(word) > 2 and word in user_question_lower:
                    score += 0.5
            
            # Check for exact matches
            if user_question_lower in question_lower or question_lower in user_question_lower:
                score += 5
            
            if user_question_lower in answer_lower or answer_lower in user_question_lower:
                score += 3
            
            # Update best match if this FAQ has higher score
            if score > best_score:
                best_score = score
                best_match = faq
        
        # Step 2: If we found a good database match, return it
        if best_match and best_score >= 2:  # Lower threshold for database matches
            return jsonify({
                'question': user_question,
                'answer': best_match.answer,
                'source': 'database_faq',
                'confidence': 'high' if best_score > 3 else 'medium',
                'found': True,
                'faq_id': best_match.id,
                'relevance_score': best_score,
                'strategy': 'database_first',
                'timestamp': datetime.now().isoformat()
            }), 200
        
        # Step 3: If no good database match, try AI service
        try:
            logger.info(f"No good database match found, trying AI service for: {user_question}")
            
            # Use AI service to generate answer based on existing FAQs
            ai_result = ai_service.smart_answer(user_question, all_faqs)
            
            return jsonify({
                'question': user_question,
                'answer': ai_result['answer'],
                'source': 'ai_service',
                'confidence': ai_result.get('confidence', 'medium'),
                'found': True,
                'strategy': 'ai_fallback',
                'similarity': ai_result.get('similarity', 0.0),
                'emotion_analysis': ai_result.get('emotion_analysis', {}),
                'requires_human': ai_result.get('requires_human', False),
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as ai_error:
            logger.error(f"AI service failed: {ai_error}")
            
            # Enhanced database fallback with better keyword matching
            if best_match and best_score > 0:
                return jsonify({
                    'question': user_question,
                    'answer': best_match.answer,
                    'source': 'database_faq_fallback',
                    'confidence': 'low',
                    'found': True,
                    'faq_id': best_match.id,
                    'relevance_score': best_score,
                    'strategy': 'database_fallback',
                    'ai_error': str(ai_error),
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                # Try to find partial matches or related topics
                partial_matches = []
                for faq in all_faqs:
                    question_lower = faq.question.lower()
                    answer_lower = faq.answer.lower()
                    
                    # Check for partial word matches
                    user_words = user_question_lower.split()
                    for word in user_words:
                        if len(word) > 3:  # Only check words longer than 3 characters
                            if word in question_lower or word in answer_lower:
                                partial_matches.append({
                                    'faq': faq,
                                    'matched_word': word,
                                    'score': 1
                                })
                
                if partial_matches:
                    # Return the best partial match
                    best_partial = max(partial_matches, key=lambda x: x['score'])
                    return jsonify({
                        'question': user_question,
                        'answer': f"While I don't have an exact answer, here's some related information: {best_partial['faq'].answer}",
                        'source': 'database_partial_match',
                        'confidence': 'low',
                        'found': True,
                        'faq_id': best_partial['faq'].id,
                        'strategy': 'partial_database_match',
                        'matched_word': best_partial['matched_word'],
                        'ai_error': str(ai_error),
                        'timestamp': datetime.now().isoformat()
                    }), 200
                else:
                    return jsonify({
                        'question': user_question,
                        'answer': 'I couldn\'t find a specific answer to your question. Here are some available topics you can ask about:',
                        'source': 'no_match',
                        'confidence': 'low',
                        'found': False,
                        'strategy': 'no_match',
                        'available_topics': [faq.question for faq in all_faqs[:8]],  # Show more topics
                        'ai_error': str(ai_error),
                        'timestamp': datetime.now().isoformat()
                    }), 200
        
    except Exception as e:
        logger.error(f"FAQ search API error: {e}")
        return jsonify({
            'question': user_question,
            'answer': 'Sorry, there was an error searching the FAQ database.',
            'source': 'error',
            'confidence': 'low',
            'error': str(e)
        }), 500

# Initialize database with PostgreSQL compatibility for Railway
def init_database():
    """Initialize database with PostgreSQL compatibility for Railway"""
    try:
        with app.app_context():
            # Test database connection with retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Test database connection
                    db.session.execute(text('SELECT 1'))
                    db.session.commit()
                    logger.info("Railway PostgreSQL database connection successful")
                    break
                except OperationalError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Railway database connection failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Railway database connection attempt {retry_count} failed, retrying... Error: {e}")
                    import time
                    time.sleep(2 ** retry_count)  # Exponential backoff
            
            # Create all tables
            db.create_all()
            logger.info("Railway database tables created successfully")
            
    except Exception as e:
        logger.error(f"Railway database initialization failed: {e}")
        raise

# Initialize database on startup
try:
    init_database()
except Exception as e:
    logger.error(f"Failed to initialize Railway database: {e}")
    # In production, you might want to exit here
    # import sys
    # sys.exit(1)

# Database connection health check
def check_db_connection():
    """Check if Railway database connection is healthy"""
    try:
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Railway database connection check failed: {e}")
        return False

# get all FAQs
@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    faqs = FAQ.query.all()
    return jsonify([faq.to_dict() for faq in faqs]), 200


# get specific FAQ by ID
@app.route('/api/faqs/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if faq:
        return jsonify(faq.to_dict()), 200
    return jsonify({"error": "FAQ not found"}), 404


# add a new FAQ
@app.route('/api/faqs', methods=['POST'])
def add_faq():
    data = request.get_json()
    
    # Check if the data is a list for batch insert
    if isinstance(data, list):
        new_faqs = []
        for item in data:
            new_faq = FAQ(question=item["question"], answer=item["answer"])
            db.session.add(new_faq)
            new_faqs.append(new_faq.to_dict())
        db.session.commit()
        return jsonify(new_faqs), 201
    else:
        new_faq = FAQ(question=data["question"], answer=data["answer"])
        db.session.add(new_faq)
        db.session.commit()
        return jsonify(new_faq.to_dict()), 201

# update an existing FAQ
@app.route('/api/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"error": "FAQ not found"}), 404

    data = request.get_json()
    if "question" in data:
        faq.question = data["question"]
    if "answer" in data:
        faq.answer = data["answer"]

    db.session.commit()
    return jsonify(faq.to_dict()), 200


# delete a FAQ
@app.route('/api/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    faq = FAQ.query.get(faq_id)
    if faq:
        db.session.delete(faq)
        db.session.commit()
        return jsonify({"message": "FAQ deleted successfully"}), 200
    return jsonify({"error": "FAQ not found"}), 404

# check if the server is running
@app.route('/')
def index():
    return jsonify({"message": "FAQ API is running"}), 200

# Log a question
@app.route('/api/log', methods=['POST'])
def log_question():
    data = request.get_json()
    question = data.get('question')
    if question:
        log = Log(question=question)
        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Logged'}), 201
    return jsonify({'error': 'No question provided'}), 400

# Get top 5 most asked question categories
@app.route('/api/top-questions')
def top_questions():
    # Count questions by category
    results = db.session.query(
        Log.category, func.count().label('count')
    ).filter(Log.category.isnot(None))\
     .group_by(Log.category)\
     .order_by(func.count().desc())\
     .limit(5).all()

    return jsonify([{'question': category, 'count': count} for category, count in results])

# Get questions by category
@app.route('/api/category-details/<category>')
def category_details(category):
    questions = db.session.query(
        Log.question, Log.keywords, Log.timestamp
    ).filter(Log.category == category)\
     .order_by(Log.timestamp.desc())\
     .limit(20).all()
    
    return jsonify([
        {
            'question': q,
            'keywords': k,
            'timestamp': t.isoformat() if t else None
        } for q, k, t in questions
    ])

# Get all categories with counts
@app.route('/api/categories')
def get_categories():
    results = db.session.query(
        Log.category, func.count().label('count')
    ).filter(Log.category.isnot(None))\
     .group_by(Log.category)\
     .order_by(func.count().desc())\
     .all()
    
    return jsonify([{'category': category, 'count': count} for category, count in results])

# Get daily question counts for the last 7 days
@app.route('/api/daily-question-counts')
def daily_counts():
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)

    results = db.session.query(
        func.date(Log.timestamp),
        func.count()
    ).filter(Log.timestamp >= start_date)\
     .group_by(func.date(Log.timestamp))\
     .order_by(func.date(Log.timestamp))\
     .all()

    return jsonify([{'date': str(d), 'count': c} for d, c in results])

# Submit feedback
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    feedback = Feedback(satisfied=data['satisfied'])
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback received"}), 201

# Get CSAT score
@app.route('/api/csat')
def get_csat():
    total = db.session.query(func.count(Feedback.id)).scalar()
    if total == 0:
        return jsonify({'csat': 0})
    
    satisfied_count = db.session.query(func.count(Feedback.id))\
                        .filter(Feedback.satisfied == True).scalar()
    
    csat_score = round((satisfied_count / total) * 100, 2)
    return jsonify({'csat': csat_score})



# AI Chat API Endpoint
@app.route('/api/chat', methods=['POST'])
def smart_chat():
    data = request.get_json()
    user_question = data.get('question', '').strip()
    session_id = data.get('session_id')  # Optional session ID
    
    if not user_question:
        return jsonify({'error': 'Question cannot be empty'}), 400
    
    try:
        # Extract keywords and classification
        keyword_result = keyword_service.process_question(user_question)
        
        # If session_id is provided, verify if session is active
        session_active = False
        if session_id:
            session_active = conversation_service.is_session_active(session_id)
            if session_active:
                conversation_service.update_session_activity(session_id)
        
        # Log user question with keywords, category and session info
        log = Log(
            question=user_question,
            keywords=keyword_result['keywords_str'],
            category=keyword_result['category'],
            session_id=session_id if session_active else None
        )
        db.session.add(log)
        db.session.commit()
        
        # Get all FAQs
        faqs = FAQ.query.all()
        
        # Use AI service to generate intelligent answer
        result = ai_service.smart_answer(user_question, faqs)
        
        response_data = {
            'question': user_question,
            'answer': result['answer'],
            'source': result['source'],
            'confidence': result['confidence'],
            'similarity': result.get('similarity', 0.0),
            'emotion_analysis': result.get('emotion_analysis', {}),
            'requires_human': result.get('requires_human', False)
        }
        
        # If there's an active session, add session information
        if session_active:
            response_data['session_id'] = session_id
            response_data['session_active'] = True
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Intelligent Chat API Error: {e}")
        db.session.rollback()  # Rollback any database changes
        return jsonify({
            'question': user_question,
            'answer': 'Sorry, the service is temporarily unavailable. Please try again later.',
            'source': 'error',
            'confidence': 'low',
            'similarity': 0.0,
            'error_details': str(e) if app.config.get('DEBUG') else 'Internal server error'
        }), 500

# User Authentication APIs
# Session management API endpoints
@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new conversation session"""
    data = request.get_json() or {}
    user_id = session.get('user_id')  # Get user ID from current login session
    
    result = conversation_service.start_session(user_id)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 500

@app.route('/api/session/end', methods=['POST'])
def end_session():
    """End conversation session and submit feedback"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    # Extract feedback data
    feedback_data = None
    if any(key in data for key in ['satisfied', 'rating', 'comment']):
        feedback_data = {
            'satisfied': data.get('satisfied', True),
            'rating': data.get('rating'),
            'comment': data.get('comment', '').strip() or None
        }
    
    result = conversation_service.end_session(session_id, feedback_data)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/session/status/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """Get session status"""
    is_active = conversation_service.is_session_active(session_id)
    session_info = conversation_service.get_session_info(session_id)
    
    if not session_info:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'is_active': is_active,
        'session_info': session_info
    }), 200

@app.route('/api/session/questions/<session_id>', methods=['GET'])
def get_session_questions(session_id):
    """Get all questions in the session"""
    questions = conversation_service.get_session_questions(session_id)
    
    return jsonify({
        'session_id': session_id,
        'questions': questions,
        'count': len(questions)
    }), 200

@app.route('/api/session/statistics', methods=['GET'])
def get_session_statistics():
    """Get session statistics"""
    stats = conversation_service.get_session_statistics()
    return jsonify(stats), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'employee').strip()
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email and password are required'}), 400
    
    if role not in ['admin', 'employee']:
        return jsonify({'error': 'Role must be admin or employee'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User {username} registered successfully")
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed for user {username}: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/current-user', methods=['GET'])
def current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify(user.to_dict()), 200
    
    return jsonify({'error': 'Not authenticated'}), 401

if __name__ == '__main__':
    # Railway环境配置
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # 在Railway上使用0.0.0.0绑定所有接口
    host = '0.0.0.0' if os.environ.get('RAILWAY_DEPLOYMENT') else '127.0.0.1'
    
    print(f"🚂 启动Railway FAQ后端服务...")
    print(f"🌐 主机: {host}")
    print(f"🔌 端口: {port}")
    print(f"🐛 调试模式: {debug}")
    
    app.run(host=host, port=port, debug=debug)