#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword extraction service test script
Used to verify keyword extraction and question classification functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from keyword_service import KeywordService

def test_keyword_extraction():
    """Test keyword extraction functionality"""
    print("🔍 Testing keyword extraction functionality")
    print("=" * 50)
    
    keyword_service = KeywordService()
    
    test_cases = [
        "How do I apply for vacation leave?",
        "how can i leave",
        "I need to reset my password",
        "Where can I find my payroll information?",
        "What are the company working hours?",
        "How do I access the VPN?",
        "I need to book a meeting room",
        "How to submit expense reimbursement?"
    ]
    
    for question in test_cases:
        result = keyword_service.process_question(question)
        print(f"\nQuestion: {question}")
        print(f"Keywords: {result['keywords']}")
        print(f"Category: {result['category']} (Confidence: {result['confidence']:.2f})")
        print(f"Keywords string: {result['keywords_str']}")

def test_categorization():
    """Test question classification functionality"""
    print("\n\n📊 Testing question classification functionality")
    print("=" * 50)
    
    keyword_service = KeywordService()
    
    # Test whether similar questions are classified into the same category
    similar_questions = [
        ["How do I apply for vacation leave?", "how can i leave", "I need time off"],
        ["I forgot my password", "How to reset password?", "Password reset help"],
        ["Where is my payroll?", "When is payday?", "Salary information"]
    ]
    
    for group in similar_questions:
        print(f"\nSimilar question group:")
        categories = []
        for question in group:
            category, confidence = keyword_service.categorize_question(question)
            categories.append(category)
            print(f"  - {question} → {category} ({confidence:.2f})")
        
        # Check if classified into the same category
        if len(set(categories)) == 1:
            print(f"  ✅ Successfully classified as: {categories[0]}")
        else:
            print(f"  ❌ Inconsistent classification: {set(categories)}")

def test_category_stats():
    """Test category statistics functionality"""
    print("\n\n📈 Testing category statistics functionality")
    print("=" * 50)
    
    keyword_service = KeywordService()
    
    test_questions = [
        "How do I apply for vacation leave?",
        "how can i leave",
        "I need time off",
        "I forgot my password",
        "How to reset password?",
        "Where is my payroll?",
        "When is payday?",
        "How do I access VPN?",
        "VPN connection issues"
    ]
    
    stats = keyword_service.get_category_stats(test_questions)
    
    print("Category statistics results:")
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} questions")

def test_edge_cases():
    """Test edge cases"""
    print("\n\n🧪 Testing edge cases")
    print("=" * 50)
    
    keyword_service = KeywordService()
    
    edge_cases = [
        "",  # Empty string
        "   ",  # Only spaces
        "a",  # Single character
        "!!!",  # Only punctuation
        "How are you?",  # General question
        "URGENT!!! I NEED HELP WITH PASSWORD!!!",  # Uppercase and punctuation
    ]
    
    for question in edge_cases:
        try:
            result = keyword_service.process_question(question)
            print(f"\nQuestion: '{question}'")
            print(f"Keywords: {result['keywords']}")
            print(f"Category: {result['category']}")
        except Exception as e:
            print(f"\nQuestion: '{question}' - Error: {e}")

if __name__ == '__main__':
    print("🚀 Keyword Extraction Service Test")
    print("=" * 60)
    
    test_keyword_extraction()
    test_categorization()
    test_category_stats()
    test_edge_cases()
    
    print("\n\n✅ Test completed!")