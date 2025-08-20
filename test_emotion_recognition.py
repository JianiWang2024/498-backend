#!/usr/bin/env python3
# Test script for emotion recognition functionality
# This script tests various emotional inputs to verify the emotion detection system

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import ai_service
from models import FAQ

def test_emotion_recognition():
    """Test emotion recognition with various user inputs"""
    
    # Test cases with different emotional states
    test_cases = [
        {
            'input': 'I am so frustrated with this system!',
            'expected_emotions': ['angry', 'frustrated']
        },
        {
            'input': 'I need help ASAP! This is urgent!',
            'expected_emotions': ['impatient']
        },
        {
            'input': 'This is terrible and useless. I want to complain!',
            'expected_emotions': ['dissatisfied', 'complaint']
        },
        {
            'input': 'Can I speak to a human agent please?',
            'expected_emotions': ['transfer']
        },
        {
            'input': 'I AM REALLY MAD ABOUT THIS!!!',
            'expected_emotions': ['frustrated']
        },
        {
            'input': 'Hello, how can I reset my password?',
            'expected_emotions': []
        },
        {
            'input': 'I hate this stupid system and want to talk to your manager immediately!',
            'expected_emotions': ['angry', 'dissatisfied', 'complaint', 'impatient']
        }
    ]
    
    print("=== Emotion Recognition Test Results ===")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        user_input = test_case['input']
        expected = test_case['expected_emotions']
        
        # Analyze emotion
        emotion_result = ai_service.analyze_emotion(user_input)
        detected = emotion_result['emotions']
        needs_human = emotion_result['needs_human']
        sentiment = emotion_result['sentiment']
        
        print(f"Test Case {i}:")
        print(f"Input: '{user_input}'")
        print(f"Expected emotions: {expected}")
        print(f"Detected emotions: {detected}")
        print(f"Emotion score: {emotion_result['emotion_score']}")
        print(f"Sentiment: {sentiment}")
        print(f"Needs human: {needs_human}")
        
        # Check if any expected emotions were detected
        if expected:
            detected_expected = any(emotion in detected for emotion in expected)
            print(f"✅ Detection successful" if detected_expected else "❌ Detection failed")
        else:
            print(f"✅ Correctly identified as neutral" if not detected else "⚠️ False positive detected")
        
        print("-" * 60)
        print()

def test_human_transfer_responses():
    """Test human transfer response generation"""
    
    print("=== Human Transfer Response Test ===")
    print()
    
    test_emotions = [
        {
            'emotions': ['complaint', 'angry'],
            'emotion_score': 3,
            'needs_human': True,
            'sentiment': 'negative'
        },
        {
            'emotions': ['transfer'],
            'emotion_score': 1,
            'needs_human': True,
            'sentiment': 'negative'
        },
        {
            'emotions': ['frustrated', 'impatient', 'dissatisfied'],
            'emotion_score': 4,
            'needs_human': True,
            'sentiment': 'negative'
        }
    ]
    
    for i, emotion_analysis in enumerate(test_emotions, 1):
        response = ai_service.generate_human_transfer_response(emotion_analysis)
        print(f"Test Case {i}:")
        print(f"Emotions: {emotion_analysis['emotions']}")
        print(f"Response: {response}")
        print("-" * 60)
        print()

def test_smart_answer_with_emotions():
    """Test the complete smart answer flow with emotion detection"""
    
    print("=== Smart Answer with Emotion Detection Test ===")
    print()
    
    # Create some sample FAQs
    sample_faqs = [
        FAQ(question="How do I reset my password?", answer="You can reset your password by visiting the IT portal and clicking 'Forgot Password'."),
        FAQ(question="What are the working hours?", answer="Our standard working hours are 9 AM to 5 PM, Monday to Friday."),
        FAQ(question="How do I apply for leave?", answer="You can apply for leave through the HR portal under 'My Leave' section.")
    ]
    
    test_inputs = [
        "I'm so frustrated! How do I reset my password?",
        "I need to complain about something. Can I speak to a manager?",
        "What are the working hours?",
        "This is urgent! I need help with leave application ASAP!"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        result = ai_service.smart_answer(user_input, sample_faqs)
        
        print(f"Test Case {i}:")
        print(f"Input: '{user_input}'")
        print(f"Answer: {result['answer']}")
        print(f"Source: {result['source']}")
        print(f"Requires Human: {result['requires_human']}")
        if 'emotion_analysis' in result:
            print(f"Detected Emotions: {result['emotion_analysis']['emotions']}")
            print(f"Sentiment: {result['emotion_analysis']['sentiment']}")
        print("-" * 60)
        print()

if __name__ == "__main__":
    print("Starting Emotion Recognition System Tests...")
    print("=" * 60)
    print()
    
    test_emotion_recognition()
    test_human_transfer_responses()
    test_smart_answer_with_emotions()
    
    print("All tests completed!")