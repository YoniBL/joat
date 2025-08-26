#!/usr/bin/env python3
"""
JOAT Model Testing Script
Tests all specialized models to ensure they're working correctly.
"""

import sys
import os
from app import JOATSystem

def test_models():
    """Test all models with sample queries."""
    
    print("🧪 JOAT Model Testing")
    print("=" * 50)
    
    # Initialize the system
    system = JOATSystem()
    
    if not system.models_mapping:
        print("❌ Error: Could not load models mapping (check models_mapping.json)")
        return
    
    print(f"✅ Loaded {len(system.models_mapping)} model mappings")
    print()
    
    # Test queries for each task type
    test_queries = {
        'coding_generation': "Write a Python function to calculate fibonacci numbers",
        'text_generation': "Write a short story about a robot learning to paint",
        'mathematical_reasoning': "Solve the equation: 3x + 7 = 22",
        'commonsense_reasoning': "Why do people wear coats in winter?",
        'question_answering': "What is the capital of Japan?",
        'dialogue_systems': "Tell me a joke",
        'summarization': "Summarize the key points of machine learning",
        'sentiment_analysis': "Analyze the sentiment of this text: 'I love this new phone!'",
        'visual_question_answering': "Describe what you would see in a sunset",
        'video_question_answering': "What happens in a typical movie scene"
    }
    
    results = {}
    
    for task_type, query in test_queries.items():
        print(f"🔍 Testing {task_type}...")
        print(f"   Query: {query}")
        print(f"   Expected model: {system.models_mapping.get(task_type, 'Unknown')}")
        
        try:
            response_data = system.process_query(query)
            resp_text = response_data.get('response', '')
            results[task_type] = {
                'success': True,
                'response': resp_text[:200] + "..." if len(resp_text) > 200 else resp_text,
                'model': response_data.get('model_used', 'Unknown')
            }
            print(f"   ✅ Success - Model: {response_data.get('model_used', 'Unknown')}")
        except Exception as e:
            results[task_type] = {
                'success': False,
                'error': str(e),
                'model': system.models_mapping.get(task_type, 'Unknown')
            }
            print(f"   ❌ Failed: {e}")
        
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    successful = [task for task, result in results.items() if result['success']]
    failed = [task for task, result in results.items() if not result['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    for task in successful:
        model = results[task]['model']
        print(f"   • {task} → {model}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{len(results)}")
        for task in failed:
            model = results[task]['model']
            error = results[task]['error']
            print(f"   • {task} → {model}: {error}")
    
    print(f"\n🎯 Overall: {len(successful)}/{len(results)} models working correctly")
    
    if len(successful) == len(results):
        print("🎉 All models are working perfectly!")
    elif len(successful) >= len(results) * 0.8:
        print("👍 Most models are working well!")
    else:
        print("⚠️  Some models need attention")

def test_specific_model(model_name: str, query: str):
    """Test a specific model with a custom query."""
    print(f"🧪 Testing {model_name} with custom query")
    print("=" * 50)
    
    system = JOATSystem()
    
    try:
        response = system.model_manager.send_query(model_name, query, history=[])
        print(f"✅ Success!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Failed: {e}")

def test_essential_mode():
    """Test essential mode fallback logic."""
    print("\n🧪 JOAT Essential Mode Fallback Test")
    print("=" * 50)
    
    # Initialize the system in essential mode
    system = JOATSystem(essential_mode=True)
    
    if not system.models_mapping:
        print("❌ Error: Could not load models mapping")
        return
    
    print(f"✅ Loaded {len(system.models_mapping)} model mappings (Essential Mode)")
    print()
    
    # Test queries for each task type
    test_queries = {
        'coding_generation': "Write a Python function to calculate fibonacci numbers",
        'text_generation': "Write a short story about a robot learning to paint",
        'mathematical_reasoning': "Solve the equation: 3x + 7 = 22",
        'commonsense_reasoning': "Why do people wear coats in winter?",
        'question_answering': "What is the capital of Japan?",
        'dialogue_systems': "Tell me a joke",
        'summarization': "Summarize the key points of machine learning",
        'sentiment_analysis': "Analyze the sentiment of this text: 'I love this new phone!'",
        'visual_question_answering': "Describe what you would see in a sunset",
        'video_question_answering': "What happens in a typical movie scene"
    }
    
    for task_type, query in test_queries.items():
        print(f"🔍 Testing {task_type} (Essential Mode)...")
        print(f"   Query: {query}")
        expected_model = system.models_mapping.get(task_type, 'Unknown')
        print(f"   Mapped model: {expected_model}")
        try:
            response_data = system.process_query(query)
            model_used = response_data.get('model_used', 'Unknown')
            response = response_data.get('response', '')
            print(f"   ✅ Used model: {model_used}")
            if '[INFO]' in response:
                print(f"   ℹ️  {response.splitlines()[0]}")
            print(f"   Response: {response[:120]}{'...' if len(response) > 120 else ''}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()

def main():
    """Main function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--model' and len(sys.argv) >= 4:
            model_name = sys.argv[2]
            query = sys.argv[3]
            test_specific_model(model_name, query)
        elif sys.argv[1] == '--essential':
            test_essential_mode()
        else:
            print("Usage: python test_models.py [--model MODEL_NAME QUERY | --essential]")
    else:
        test_models()

if __name__ == "__main__":
    main() 