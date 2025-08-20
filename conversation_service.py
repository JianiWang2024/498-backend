#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversation Management Service
Handles session creation, management and termination for continuous conversation functionality
"""

import uuid
from datetime import datetime, timedelta
from models import db, ConversationSession, Log, Feedback
from sqlalchemy import func

class ConversationService:
    def __init__(self):
        self.session_timeout_minutes = 30  # Session timeout in minutes
        self.max_questions_per_session = 50  # Maximum questions per session
    
    def start_session(self, user_id=None):
        """
        Start a new conversation session
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            dict: Dictionary containing session_id and session information
        """
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create new session record
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.utcnow(),
                is_active=True,
                question_count=0
            )
            
            db.session.add(session)
            db.session.commit()
            
            return {
                'success': True,
                'session_id': session_id,
                'session_info': session.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to start session: {str(e)}'
            }
    
    def end_session(self, session_id, feedback_data=None):
        """
        End conversation session and process feedback
        
        Args:
            session_id: Session ID
            feedback_data: Feedback data dictionary containing satisfied, rating, comment, etc.
            
        Returns:
            dict: Operation result
        """
        try:
            # Find session
            session = ConversationSession.query.filter_by(
                session_id=session_id, 
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found or already ended'
                }
            
            # Update session status
            session.is_active = False
            session.end_time = datetime.utcnow()
            
            # Process feedback data
            if feedback_data:
                feedback = Feedback(
                    session_id=session_id,
                    satisfied=feedback_data.get('satisfied', True),
                    rating=feedback_data.get('rating'),
                    comment=feedback_data.get('comment'),
                    timestamp=datetime.utcnow()
                )
                db.session.add(feedback)
            
            # Mark session end log
            end_log = Log(
                question='[SESSION_END]',
                session_id=session_id,
                is_session_end=True,
                timestamp=datetime.utcnow()
            )
            db.session.add(end_log)
            
            db.session.commit()
            
            return {
                'success': True,
                'session_info': session.to_dict(),
                'feedback_recorded': feedback_data is not None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to end session: {str(e)}'
            }
    
    def is_session_active(self, session_id):
        """
        Check if session is still active
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: Whether session is active
        """
        if not session_id:
            return False
            
        session = ConversationSession.query.filter_by(
            session_id=session_id,
            is_active=True
        ).first()
        
        if not session:
            return False
        
        # Check if session has timed out
        timeout_time = session.start_time + timedelta(minutes=self.session_timeout_minutes)
        if datetime.utcnow() > timeout_time:
            # Automatically end timed out session
            self.end_session(session_id)
            return False
        
        return True
    
    def get_session_info(self, session_id):
        """
        Get session information
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Session information
        """
        session = ConversationSession.query.filter_by(
            session_id=session_id
        ).first()
        
        if not session:
            return None
        
        return session.to_dict()
    
    def get_session_questions(self, session_id):
        """
        Get all questions in the session
        
        Args:
            session_id: Session ID
            
        Returns:
            list: List of questions
        """
        questions = Log.query.filter_by(
            session_id=session_id
        ).filter(
            Log.is_session_end == False
        ).order_by(Log.timestamp).all()
        
        return [{
            'id': q.id,
            'question': q.question,
            'keywords': q.keywords,
            'category': q.category,
            'timestamp': q.timestamp.isoformat() if q.timestamp else None
        } for q in questions]
    
    def update_session_activity(self, session_id):
        """
        Update session activity status (increment question count)
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: Whether update was successful
        """
        try:
            session = ConversationSession.query.filter_by(
                session_id=session_id,
                is_active=True
            ).first()
            
            if session:
                session.question_count += 1
                
                # Check if maximum question limit is exceeded
                if session.question_count >= self.max_questions_per_session:
                    self.end_session(session_id, {
                        'satisfied': True,
                        'comment': 'Session ended due to question limit reached'
                    })
                    return False
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            return False
    
    def get_session_statistics(self):
        """
        Get session statistics
        
        Returns:
            dict: Statistics information
        """
        try:
            # Total sessions
            total_sessions = ConversationSession.query.count()
            
            # Active sessions
            active_sessions = ConversationSession.query.filter_by(is_active=True).count()
            
            # Average questions per session
            avg_questions = db.session.query(
                func.avg(ConversationSession.question_count)
            ).filter(
                ConversationSession.is_active == False
            ).scalar() or 0
            
            # Today's sessions
            today = datetime.utcnow().date()
            today_sessions = ConversationSession.query.filter(
                func.date(ConversationSession.start_time) == today
            ).count()
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'average_questions_per_session': round(float(avg_questions), 2),
                'today_sessions': today_sessions
            }
            
        except Exception as e:
            return {
                'error': f'Failed to get statistics: {str(e)}'
            }

# Create global service instance
conversation_service = ConversationService()