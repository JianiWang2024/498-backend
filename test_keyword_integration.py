#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword extraction integration test script
Test complete keyword extraction and classification functionality, including API endpoints
"""

import requests
import json
import time

# 测试配置
base_url = "https://your-railway-app.railway.app"  # 替换为你的Railway应用URL

def test_chat_api_with_keywords():
    """Test chat API keyword extraction functionality"""
    print("🤖 Testing chat API keyword extraction functionality")
    print("=" * 50)
    
    test_questions = [
        "How do I apply for vacation leave?",
        "how can i leave",
        "I forgot my password",
        "How to reset my password?",
        "Where can I find my payroll information?",
        "When is payday?",
        "What are the company working hours?",
        "How do I access the VPN?",
        "I need to book a meeting room",
        "How to submit expense reimbursement?"
    ]
    
    for question in test_questions:
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nQuestion: {question}")
                print(f"Answer: {data.get('answer', 'N/A')[:100]}...")
                print(f"Source: {data.get('source', 'N/A')}")
                print(f"Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"\nQuestion: {question} - API error: {response.status_code}")
                
        except Exception as e:
            print(f"\nQuestion: {question} - Request error: {e}")
        
        time.sleep(0.5)  # Avoid too frequent requests

def test_top_questions_api():
    """Test popular questions classification API"""
    print("\n\n📊 Testing popular questions classification API")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/top-questions")
        
        if response.status_code == 200:
            data = response.json()
            print("Popular questions classification:")
            for item in data:
                print(f"  - {item['question']}: {item['count']} times")
        else:
            print(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"Request error: {e}")

def test_categories_api():
    """Test category statistics API"""
    print("\n\n📈 Testing category statistics API")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/categories")
        
        if response.status_code == 200:
            data = response.json()
            print("All category statistics:")
            for item in data:
                print(f"  - {item['category']}: {item['count']} questions")
        else:
            print(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"Request error: {e}")

def test_category_details_api():
    """Test category details API"""
    print("\n\n🔍 Testing category details API")
    print("=" * 50)
    
    # First get all categories
    try:
        response = requests.get(f"{base_url}/api/categories")
        
        if response.status_code == 200:
            categories = response.json()
            
            # Test details of first 3 categories
            for category_info in categories[:3]:
                category = category_info['category']
                print(f"\nCategory: {category}")
                
                detail_response = requests.get(f"{base_url}/api/category-details/{category}")
                
                if detail_response.status_code == 200:
                    details = detail_response.json()
                    print(f"  Questions in this category ({len(details)} total):")
                    for detail in details[:5]:  # Only show first 5
                        print(f"    - {detail['question']}")
                        if detail['keywords']:
                            print(f"      Keywords: {detail['keywords']}")
                else:
                    print(f"  Details API error: {detail_response.status_code}")
        else:
            print(f"Categories API error: {response.status_code}")
            
    except Exception as e:
        print(f"Request error: {e}")

def test_server_connection():
    """Test server connection"""
    print("🔗 Testing server connection")
    print("=" * 50)
    
    try:
        response = requests.get(base_url)
        
        if response.status_code == 200:
            print("✅ Server connection normal")
            return True
        else:
            print(f"❌ Server response error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Keyword extraction integration test")
    print("=" * 60)
    
    # First test server connection
    if test_server_connection():
        print("\nStarting integration tests...\n")
        
        # Test chat API
        test_chat_api_with_keywords()
        
        # Wait for database update
        time.sleep(2)
        
        # Test statistics API
        test_top_questions_api()
        test_categories_api()
        test_category_details_api()
        
        print("\n\n✅ Integration test completed!")
    else:
        print("\n❌ Unable to connect to server, please ensure backend service is running")