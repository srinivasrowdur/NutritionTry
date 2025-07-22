#!/usr/bin/env python3
"""
Test script to demonstrate the improved PDF Chat Agent with knowledge base constraints.
This script shows how the agent now properly handles questions outside the PDF scope.
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "https://pdf-chat-api-qy3lqavtda-uc.a.run.app"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✅ {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        print("-" * 50)
        return response
        
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {str(e)}")
        print("-" * 50)
        return None

def test_chat_questions():
    """Test various types of questions to demonstrate constraint behavior"""
    
    # Test questions - mix of PDF-related and general questions
    test_questions = [
        {
            "category": "PDF Content Question",
            "question": "What are the main topics covered in the uploaded PDF documents?",
            "expected": "Should provide information about PDF content"
        },
        {
            "category": "General Knowledge Question",
            "question": "What is the capital of France?",
            "expected": "Should reject - outside PDF scope"
        },
        {
            "category": "Technical Question",
            "question": "How do I install Python on my computer?",
            "expected": "Should reject - outside PDF scope"
        },
        {
            "category": "PDF Content Question",
            "question": "Can you summarize the key points from the documents?",
            "expected": "Should provide PDF summary"
        },
        {
            "category": "Unrelated Question",
            "question": "What's the weather like today?",
            "expected": "Should reject - outside PDF scope"
        }
    ]
    
    print("🧪 Testing Chat Endpoint with Various Questions")
    print("=" * 60)
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{i}. {test['category']}")
        print(f"Question: {test['question']}")
        print(f"Expected: {test['expected']}")
        
        response = test_endpoint("/chat", method="POST", data={
            "message": test['question']
        })
        
        if response and response.status_code == 200:
            result = response.json()
            print(f"Actual Response: {result.get('response', 'No response')[:200]}...")
        
        time.sleep(1)  # Small delay between requests

def main():
    """Main test function"""
    print("🚀 PDF Chat Agent Constraint Testing")
    print("=" * 60)
    
    # Test basic endpoints
    print("\n1. Testing Basic Endpoints")
    test_endpoint("/health")
    test_endpoint("/pdfs")
    
    # Test chat functionality
    print("\n2. Testing Chat Constraints")
    test_chat_questions()
    
    print("\n✅ Testing Complete!")
    print("\n📋 Summary:")
    print("• The agent should now only answer questions about PDF content")
    print("• General knowledge questions should be politely rejected")
    print("• Use /pdfs endpoint to see available documents")
    print("• Use /docs endpoint for interactive API testing")

if __name__ == "__main__":
    main() 