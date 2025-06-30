#!/usr/bin/env python3
"""
Example usage of the JOAT system.
This script demonstrates how to use the JOAT system programmatically.
"""

from main import JOATSystem

def example_usage():
    """Demonstrate various use cases of the JOAT system."""
    
    # Initialize the system
    print("Initializing JOAT system...")
    system = JOATSystem()
    
    if not system.models_mapping:
        print("❌ Error: Could not load models mapping. Please check the models_mapping.txt file.")
        return
    
    print(f"✅ Loaded {len(system.models_mapping)} model mappings")
    print()
    
    # Example queries for different task types
    example_queries = [
        {
            "task": "Coding Generation",
            "query": "Write a Python function to calculate the factorial of a number"
        },
        {
            "task": "Mathematical Reasoning", 
            "query": "Solve the equation: 3x + 7 = 22"
        },
        {
            "task": "Question Answering",
            "query": "What is the capital of Japan?"
        },
        {
            "task": "Text Generation",
            "query": "Write a short story about a robot learning to paint"
        },
        {
            "task": "Summarization",
            "query": "Summarize the key points of machine learning"
        }
    ]
    
    print("🤖 JOAT System Examples")
    print("=" * 50)
    
    for i, example in enumerate(example_queries, 1):
        print(f"\n{i}. {example['task']}")
        print(f"Query: {example['query']}")
        print("Processing...")
        
        try:
            response = system.process_query(example['query'])
            print(f"Response: {response[:200]}...")  # Show first 200 characters
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 30)
    
    # Demonstrate conversation continuity
    print("\n🔄 Conversation Continuity Example")
    print("=" * 50)
    
    # Start a coding conversation
    print("Starting a coding conversation...")
    response1 = system.process_query("Write a function to check if a number is prime")
    print(f"Response: {response1[:100]}...")
    
    # Continue the conversation
    print("\nContinuing the conversation...")
    response2 = system.process_query("Can you optimize this function?")
    print(f"Response: {response2[:100]}...")
    
    # Show conversation history
    print("\n📜 Conversation History:")
    history = system.get_conversation_history()
    for i, msg in enumerate(history[-6:], 1):  # Show last 6 messages
        role = "🤖" if msg["role"] == "assistant" else "👤"
        print(f"{i}. {role} {msg['content'][:80]}...")
    
    print("\n✅ Example completed!")

def test_task_classification():
    """Test the task classification system."""
    
    print("\n🧪 Task Classification Test")
    print("=" * 50)
    
    system = JOATSystem()
    
    test_queries = [
        "Write a Python script",
        "What is 2 + 2?",
        "Tell me about quantum physics",
        "Analyze the sentiment of this text",
        "Create a story about space",
        "Debug this code",
        "Summarize this article",
        "How do I cook pasta?",
        "Explain machine learning",
        "What's the weather like?"
    ]
    
    for query in test_queries:
        task_type = system.task_classifier.classify_task(query)
        model = system.models_mapping.get(task_type, "Unknown")
        print(f"Query: {query}")
        print(f"Classified as: {task_type} -> {model}")
        print("-" * 40)

if __name__ == "__main__":
    print("🚀 JOAT System Examples")
    print("=" * 60)
    
    # Run the main example
    example_usage()
    
    # Run the classification test
    test_task_classification()
    
    print("\n🎉 All examples completed!")
    print("\nTo run the interactive version, use: python main.py") 