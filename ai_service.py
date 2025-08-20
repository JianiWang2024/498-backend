# AI Intelligent Customer Service Module
# Integrates OpenAI API and semantic search functionality

import openai
import os
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
from models import FAQ
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        # Set OpenAI API key
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Initialize TF-IDF vectorizer for semantic similarity calculation
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        # Cache FAQ vectors
        self.faq_vectors = None
        self.faq_questions = []
        self.faq_answers = []
        
        # Emotion detection keywords
        self.negative_emotion_keywords = {
            'angry': ['angry', 'mad', 'furious', 'pissed', 'irritated', 'annoyed', 'frustrated'],
            'impatient': ['hurry', 'urgent', 'asap', 'immediately', 'quickly', 'fast', 'now', 'waiting too long'],
            'dissatisfied': ['terrible', 'awful', 'horrible', 'useless', 'stupid', 'worst', 'hate', 'disappointed'],
            'complaint': ['complain', 'complaint', 'report', 'escalate', 'manager', 'supervisor'],
            'transfer': ['human', 'person', 'agent', 'representative', 'transfer', 'speak to someone', 'talk to someone']
        }
        
    def update_faq_vectors(self, faqs: List[FAQ]):
        """Update FAQ vector cache"""
        if not faqs:
            return
            
        self.faq_questions = [faq.question for faq in faqs]
        self.faq_answers = [faq.answer for faq in faqs]
        
        # Calculate TF-IDF vectors
        self.faq_vectors = self.vectorizer.fit_transform(self.faq_questions)
    
    def find_similar_faq(self, user_question: str, threshold: float = 0.3) -> Dict[str, Any]:
        """Find the most relevant FAQ using semantic similarity"""
        if self.faq_vectors is None or len(self.faq_questions) == 0:
            return None
            
        # Convert user question to vector
        user_vector = self.vectorizer.transform([user_question])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_vector, self.faq_vectors)[0]
        
        # Find the most similar FAQ
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        if best_similarity >= threshold:
            return {
                'question': self.faq_questions[best_match_idx],
                'answer': self.faq_answers[best_match_idx],
                'similarity': float(best_similarity),
                'confidence': 'high' if best_similarity > 0.7 else 'medium'
            }
        
        return None
    
    def analyze_emotion(self, user_message: str) -> Dict[str, Any]:
        """Analyze user emotion and detect negative sentiment"""
        user_message_lower = user_message.lower()
        detected_emotions = []
        emotion_score = 0
        
        # Check for negative emotion keywords
        for emotion_type, keywords in self.negative_emotion_keywords.items():
            for keyword in keywords:
                if keyword in user_message_lower:
                    detected_emotions.append(emotion_type)
                    emotion_score += 1
        
        # Check for excessive punctuation (indicating frustration)
        exclamation_count = user_message.count('!')
        question_count = user_message.count('?')
        caps_ratio = sum(1 for c in user_message if c.isupper()) / len(user_message) if user_message else 0
        
        if exclamation_count > 2 or caps_ratio > 0.5:
            detected_emotions.append('frustrated')
            emotion_score += 1
        
        # Determine if user needs human assistance
        needs_human = any(emotion in detected_emotions for emotion in ['complaint', 'transfer']) or emotion_score >= 3
        
        return {
            'emotions': list(set(detected_emotions)),
            'emotion_score': emotion_score,
            'needs_human': needs_human,
            'sentiment': 'negative' if emotion_score > 0 else 'neutral'
        }
    
    def generate_human_transfer_response(self, emotion_analysis: Dict[str, Any]) -> str:
        """Generate appropriate response for human transfer"""
        base_message = "I understand your concern and I want to make sure you get the best possible help. "
        
        if 'complaint' in emotion_analysis['emotions'] or 'transfer' in emotion_analysis['emotions']:
            return base_message + "Let me connect you with one of our human customer service representatives who can assist you further. Please hold on while I transfer your request."
        
        if emotion_analysis['emotion_score'] >= 3:
            return base_message + "I can see this is important to you. I'm connecting you with a human agent who can provide more personalized assistance. Thank you for your patience."
        
        return base_message + "I'm arranging for a human representative to assist you. They will be with you shortly."
    
    def generate_ai_response(self, user_question: str, context_faqs: List[str] = None) -> str:
        """Generate intelligent response using OpenAI"""
        if not self.openai_api_key:
            return "AI service is temporarily unavailable. Please contact administrator to configure API key."
        
        try:
            # Build context
            context = ""
            if context_faqs:
                context = "\n\nRelevant FAQ information:\n" + "\n".join(context_faqs)
            
            # Build prompt
            system_prompt = """
You are a professional enterprise internal AI customer service assistant. Please provide accurate and helpful answers based on user questions and provided FAQ information.

Answer requirements:
1. If there is relevant information in the FAQ, prioritize using FAQ content to answer
2. If there is no complete match in the FAQ, provide reasonable suggestions based on common sense and professional knowledge
3. Answers should be concise and clear, with a friendly and professional tone
4. If the answer cannot be determined, suggest users contact relevant departments
5. Answer in English
            """
            
            user_prompt = f"User question: {user_question}{context}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7,
                api_base="https://api.chatanywhere.org/v1"
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            print(f"API Key configured: {'Yes' if self.openai_api_key else 'No'}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            return "Sorry, AI service is temporarily unavailable. Please try again later or contact technical support."
    
    def smart_answer(self, user_question: str, faqs: List[FAQ]) -> Dict[str, Any]:
        """Main intelligent answer function with emotion analysis"""
        # First, analyze user emotion
        emotion_analysis = self.analyze_emotion(user_question)
        
        # If user needs human assistance, prioritize human transfer
        if emotion_analysis['needs_human']:
            human_response = self.generate_human_transfer_response(emotion_analysis)
            return {
                'answer': human_response,
                'source': 'human_transfer',
                'confidence': 'high',
                'similarity': 0.0,
                'emotion_analysis': emotion_analysis,
                'requires_human': True
            }
        
        # Update FAQ vectors (if needed)
        if self.faq_vectors is None or len(self.faq_questions) != len(faqs):
            self.update_faq_vectors(faqs)
        
        # Try semantic matching
        similar_faq = self.find_similar_faq(user_question)
        
        if similar_faq and similar_faq['confidence'] == 'high':
            # High confidence match, return FAQ answer directly
            answer = similar_faq['answer']
            
            # Add empathetic response if negative emotion detected
            if emotion_analysis['sentiment'] == 'negative':
                answer = "I understand this might be frustrating. " + answer + "\n\nIf you need further assistance, please let me know and I can connect you with a human representative."
            
            return {
                'answer': answer,
                'source': 'faq_match',
                'confidence': similar_faq['confidence'],
                'similarity': similar_faq['similarity'],
                'emotion_analysis': emotion_analysis,
                'requires_human': False
            }
        
        # Medium confidence or no match, use AI to generate answer
        context_faqs = []
        if similar_faq:
            context_faqs.append(f"Q: {similar_faq['question']}\nA: {similar_faq['answer']}")
        
        # Add other relevant FAQs as context
        if self.faq_vectors is not None:
            user_vector = self.vectorizer.transform([user_question])
            similarities = cosine_similarity(user_vector, self.faq_vectors)[0]
            
            # Get top 3 most similar FAQs as context
            top_indices = np.argsort(similarities)[-3:][::-1]
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum relevance threshold
                    context_faqs.append(f"Q: {self.faq_questions[idx]}\nA: {self.faq_answers[idx]}")
        
        ai_answer = self.generate_ai_response(user_question, context_faqs[:3])  # Limit context length
        
        # Add empathetic response if negative emotion detected
        if emotion_analysis['sentiment'] == 'negative':
            ai_answer = "I understand your concern. " + ai_answer + "\n\nIf this doesn't fully address your issue, I can connect you with a human representative for more personalized assistance."
        
        return {
            'answer': ai_answer,
            'source': 'ai_generated',
            'confidence': 'medium' if similar_faq else 'low',
            'similarity': similar_faq['similarity'] if similar_faq else 0.0,
            'emotion_analysis': emotion_analysis,
            'requires_human': False
        }

# Global AI service instance
ai_service = AIService()