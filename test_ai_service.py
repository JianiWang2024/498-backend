# AI Service Test Script
# For validating intelligent customer service functionality

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from models import FAQ
from app import app
import json

def test_ai_service():
    """Test various functions of AI service"""
    
    print("🤖 AI Intelligent Customer Service Test")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    # Create test FAQ data
    test_faqs = [
        FAQ(id=1, question="How do I apply for vacation leave?", 
            answer="You can apply for vacation leave through the HR portal under 'Leave Management'."),
        FAQ(id=2, question="How to reset my password?", 
            answer="Go to the IT self-service portal and click 'Reset Password'."),
        FAQ(id=3, question="Where can I find my payroll information?", 
            answer="Your payroll information is available in the Employee Self-Service portal."),
        FAQ(id=4, question="What are the company working hours?", 
            answer="Standard working hours are Monday to Friday, 9:00 AM to 5:00 PM."),
    ]
    
    # Test cases
    test_cases = [
        {
            "question": "How do I apply for vacation leave?",
            "expected": "exact_match",
            "description": "Exact match test"
        },
        {
            "question": "How can I request time off?",
            "expected": "semantic_match",
            "description": "Semantic similarity match test"
        },
        {
            "question": "I forgot my login password, what should I do?",
            "expected": "semantic_match",
            "description": "Semantic understanding test"
        },
        {
            "question": "What time does the office open?",
            "expected": "semantic_match",
            "description": "Related question match test"
        },
        {
            "question": "How do I cook pasta?",
            "expected": "no_match",
            "description": "Irrelevant question test"
        }
    ]
    
    print("\nTest Results:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Question: {test_case['question']}")
        
        try:
            # Call AI service
            result = ai_service.smart_answer(test_case['question'], test_faqs)
            
            print(f"Answer: {result['answer'][:100]}..." if len(result['answer']) > 100 else f"Answer: {result['answer']}")
            print(f"Source: {result['source']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Similarity: {result.get('similarity', 0):.3f}")
            
            # Evaluate results
            if result['source'] == 'faq_match' and test_case['expected'] in ['exact_match', 'semantic_match']:
                print("✅ Test passed")
            elif result['source'] == 'ai_generated' and test_case['expected'] == 'no_match':
                print("✅ Test passed")
            elif result['source'] == 'ai_generated' and test_case['expected'] == 'semantic_match':
                print("⚠️  AI generated answer (acceptable)")
            else:
                print("❌ Test result does not meet expectations")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed")

def test_similarity_function():
    """Test semantic similarity functionality"""
    
    print("\nSemantic Similarity Test")
    print("=" * 50)
    
    ai_service = AIService()
    
    # Create test FAQs
    test_faqs = [
        FAQ(id=1, question="How do I apply for vacation leave?", 
            answer="You can apply through the HR portal."),
        FAQ(id=2, question="How to reset my password?", 
            answer="Go to IT self-service portal."),
    ]
    
    ai_service.update_faq_vectors(test_faqs)
    
    # Test similarity calculation
    similarity_tests = [
        "How do I apply for vacation leave?",  # Exact match
        "How can I request time off?",         # Semantic similarity
        "I want to take a vacation",           # Related concept
        "How to reset password?",              # Slightly different
        "I forgot my login credentials",       # Semantically related
        "What's the weather like?",            # Completely unrelated
    ]
    
    for question in similarity_tests:
        result = ai_service.find_similar_faq(question)
        if result:
            print(f"Question: {question}")
            print(f"Match: {result['question']}")
            print(f"Similarity: {result['similarity']:.3f}")
            print(f"Confidence: {result['confidence']}")
            print("-" * 30)
        else:
            print(f"Question: {question}")
            print("No match found")
            print("-" * 30)

def check_dependencies():
    """Check if dependency packages are correctly installed"""
    
    print("Dependency Check")
    print("=" * 50)
    
    dependencies = [
        ('sklearn', 'scikit-learn'),
        ('numpy', 'numpy'),
        ('openai', 'openai'),
    ]
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Not installed")
            print(f"   Please run: pip install {package}")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API Key - Configured")
    else:
        print(f"⚠️  OpenAI API Key - Not configured")
        print(f"   Please set OPENAI_API_KEY in .env file")

if __name__ == '__main__':
    print("AI Intelligent Customer Service System Test Suite")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Test semantic similarity
    test_similarity_function()
    
    # Test AI service
    test_ai_service()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Tips:")
    print("- If OpenAI API is not configured, the system will use semantic matching mode")
    print("- It is recommended to configure API key for optimal AI response quality")
    print("- You can optimize matching performance by adjusting similarity threshold")