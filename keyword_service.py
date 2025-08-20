#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword extraction and question classification service
Used to extract keywords from user questions and perform intelligent classification
"""

import re
from typing import List, Dict, Tuple

class KeywordService:
    def __init__(self):
        # Define question categories and related keywords
        self.category_keywords = {
            'vacation_leave': {
                'keywords': ['vacation', 'leave', 'time off', 'holiday', 'pto', 'paid time off', 'annual leave'],
                'patterns': [r'\b(vacation|leave|time\s+off|holiday|pto)\b'],
                'category_name': 'vacation leave'
            },
            'password_reset': {
                'keywords': ['password', 'reset', 'login', 'forgot', 'change password', 'unlock'],
                'patterns': [r'\b(password|reset|login|forgot)\b'],
                'category_name': 'password reset'
            },
            'payroll': {
                'keywords': ['payroll', 'salary', 'pay', 'paycheck', 'payday', 'wages'],
                'patterns': [r'\b(payroll|salary|pay|paycheck|payday|wages)\b'],
                'category_name': 'payroll'
            },
            'working_hours': {
                'keywords': ['working hours', 'work time', 'schedule', 'hours', 'office hours'],
                'patterns': [r'\b(working\s+hours|work\s+time|schedule|hours)\b'],
                'category_name': 'working hours'
            },
            'vpn_access': {
                'keywords': ['vpn', 'remote access', 'connection', 'network'],
                'patterns': [r'\b(vpn|remote\s+access|connection|network)\b'],
                'category_name': 'vpn access'
            },
            'meeting_room': {
                'keywords': ['meeting room', 'book room', 'reserve room', 'conference room'],
                'patterns': [r'\b(meeting\s+room|book\s+room|reserve\s+room|conference\s+room)\b'],
                'category_name': 'meeting room'
            },
            'expense_reimbursement': {
                'keywords': ['expense', 'reimbursement', 'reimburse', 'receipt'],
                'patterns': [r'\b(expense|reimbursement|reimburse|receipt)\b'],
                'category_name': 'expense reimbursement'
            },
            'training': {
                'keywords': ['training', 'course', 'learning', 'education'],
                'patterns': [r'\b(training|course|learning|education)\b'],
                'category_name': 'training'
            },
            'it_support': {
                'keywords': ['it support', 'technical', 'software', 'computer', 'system'],
                'patterns': [r'\b(it\s+support|technical|software|computer|system)\b'],
                'category_name': 'it support'
            },
            'hr_general': {
                'keywords': ['hr', 'human resources', 'employee', 'handbook', 'policy'],
                'patterns': [r'\b(hr|human\s+resources|employee|handbook|policy)\b'],
                'category_name': 'hr general'
            }
        }
        
        # Stop words list
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'can', 'could', 'should', 'would', 'will', 'shall'
        }
    
    def extract_keywords(self, question: str) -> List[str]:
        """
        Extract keywords from question
        
        Args:
            question: User question
            
        Returns:
            List of extracted keywords
        """
        # Convert to lowercase
        question_lower = question.lower()
        
        # Remove punctuation, keep letters, numbers and spaces
        cleaned_question = re.sub(r'[^a-zA-Z0-9\s]', ' ', question_lower)
        
        # Tokenize
        words = cleaned_question.split()
        
        # Remove stop words and short words
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Remove duplicates while maintaining order
        unique_keywords = []
        for keyword in keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def categorize_question(self, question: str) -> Tuple[str, float]:
        """
        Categorize the question
        
        Args:
            question: User question
            
        Returns:
            (category name, matching confidence)
        """
        question_lower = question.lower()
        best_category = 'general'
        best_score = 0.0
        
        for category_key, category_info in self.category_keywords.items():
            score = 0.0
            
            # Check keyword matching
            for keyword in category_info['keywords']:
                if keyword.lower() in question_lower:
                    score += 1.0
            
            # Check regex pattern matching
            for pattern in category_info['patterns']:
                if re.search(pattern, question_lower, re.IGNORECASE):
                    score += 1.5  # Pattern matching has higher weight
            
            # Calculate relative score
            max_possible_score = len(category_info['keywords']) + len(category_info['patterns']) * 1.5
            relative_score = score / max_possible_score if max_possible_score > 0 else 0
            
            if relative_score > best_score:
                best_score = relative_score
                best_category = category_info['category_name']
        
        return best_category, best_score
    
    def process_question(self, question: str) -> Dict[str, any]:
        """
        Process question, extract keywords and classify
        
        Args:
            question: User question
            
        Returns:
            Dictionary containing keywords and classification information
        """
        keywords = self.extract_keywords(question)
        category, confidence = self.categorize_question(question)
        
        return {
            'keywords': keywords,
            'keywords_str': ', '.join(keywords),  # For database storage
            'category': category,
            'confidence': confidence,
            'original_question': question
        }
    
    def get_category_stats(self, questions: List[str]) -> Dict[str, int]:
        """
        Get question category statistics
        
        Args:
            questions: List of questions
            
        Returns:
            Category statistics dictionary
        """
        category_counts = {}
        
        for question in questions:
            category, _ = self.categorize_question(question)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts

# Create global instance
keyword_service = KeywordService()