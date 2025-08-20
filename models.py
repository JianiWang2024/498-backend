# Create a database design and tables for the Capstone project application.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True)  # Store extracted keywords
    category = db.Column(db.String(100), nullable=True)  # Store question category
    session_id = db.Column(db.String(255), nullable=True)  # Session ID
    is_session_end = db.Column(db.Boolean, default=False)  # Whether it's a session end marker
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ConversationSession(db.Model):
    __tablename__ = 'conversation_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    question_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_active": self.is_active,
            "question_count": self.question_count
        }

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    satisfied = db.Column(db.Boolean, nullable=False)
    session_id = db.Column(db.String(255), nullable=True)  # Associated with session
    rating = db.Column(db.Integer, nullable=True)  # 1-5 star rating
    comment = db.Column(db.Text, nullable=True)  # User comment
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'admin' or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

