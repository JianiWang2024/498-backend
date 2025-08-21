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

app.config.from_object(Config)

# initialize the database
db.init_app(app)

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
        print(f"Intelligent Chat API Error: {e}")
        return jsonify({
            'question': user_question,
            'answer': 'Sorry, the service is temporarily unavailable. Please try again later.',
            'source': 'error',
            'confidence': 'low',
            'similarity': 0.0
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
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

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