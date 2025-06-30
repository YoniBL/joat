#!/usr/bin/env python3
"""
JOAT - Just One AI Tool
A multi-model conversation system that routes queries to appropriate models based on task type.
Now using local Ollama models for cost-effective operation.
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests
from datetime import datetime
import logging
from ollama_client import OllamaClient, OllamaModelManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Conversation:
    """Represents a conversation with a specific model."""
    model_name: str
    messages: List[Dict[str, str]]
    created_at: datetime
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.messages.append({"role": role, "content": content})
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get conversation context for API calls."""
        return self.messages.copy()

class TaskClassifier:
    """Classifies user queries into task types."""
    
    def __init__(self):
        self.task_keywords = {
            'coding_generation': [
                'code', 'program', 'function', 'class', 'algorithm', 'debug', 'fix', 'implement',
                'create a script', 'write code', 'coding', 'programming', 'software', 'development'
            ],
            'text_generation': [
                'write', 'generate', 'create text', 'story', 'article', 'essay', 'content',
                'compose', 'draft', 'text generation', 'creative writing'
            ],
            'mathematical_reasoning': [
                'solve', 'calculate', 'math', 'mathematics', 'equation', 'formula', 'problem',
                'arithmetic', 'algebra', 'geometry', 'statistics', 'probability'
            ],
            'commonsense_reasoning': [
                'why', 'how', 'explain', 'reason', 'logic', 'common sense', 'understanding',
                'concept', 'principle', 'theory', 'reasoning'
            ],
            'question_answering': [
                'what is', 'who is', 'where is', 'when', 'which', 'answer', 'question',
                'information', 'fact', 'knowledge', 'definition'
            ],
            'dialogue_systems': [
                'chat', 'conversation', 'talk', 'discuss', 'opinion', 'advice', 'help',
                'conversational', 'interactive', 'dialogue'
            ],
            'summarization': [
                'summarize', 'summary', 'brief', 'overview', 'condense', 'extract',
                'key points', 'main points', 'gist'
            ],
            'sentiment_analysis': [
                'sentiment', 'emotion', 'feeling', 'mood', 'tone', 'attitude', 'opinion',
                'positive', 'negative', 'neutral', 'analyze sentiment'
            ],
            'visual_question_answering': [
                'image', 'picture', 'photo', 'visual', 'see', 'look at', 'describe image',
                'what do you see', 'image analysis', 'computer vision'
            ],
            'video_question_answering': [
                'video', 'movie', 'clip', 'footage', 'motion', 'action', 'scene',
                'video analysis', 'what happens in', 'describe video'
            ]
        }
    
    def classify_task(self, query: str) -> str:
        """Classify the user query into a task type."""
        query_lower = query.lower()
        
        # Count keyword matches for each task type
        task_scores = {}
        for task_type, keywords in self.task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            task_scores[task_type] = score
        
        # Find the task type with the highest score
        if task_scores:
            best_task = max(task_scores, key=task_scores.get)
            if task_scores[best_task] > 0:
                return best_task
        
        # Default to dialogue_systems if no clear classification
        return 'dialogue_systems'

class LocalModelManager:
    """Manages local Ollama model interactions."""
    
    def __init__(self, models_mapping: Dict[str, str]):
        self.models_mapping = models_mapping
        self.conversations: Dict[str, Conversation] = {}
        self.ollama_client = OllamaClient()
        self.model_manager = OllamaModelManager()
        
        # Check if Ollama is running
        if not self.ollama_client.is_ollama_running():
            logger.warning("Ollama is not running. Please start Ollama first.")
    
    def get_or_create_conversation(self, model_name: str) -> Conversation:
        """Get existing conversation or create a new one for the model."""
        if model_name not in self.conversations:
            self.conversations[model_name] = Conversation(
                model_name=model_name,
                messages=[],
                created_at=datetime.now()
            )
        return self.conversations[model_name]
    
    def send_query(self, model_name: str, query: str) -> str:
        """Send a query to the specified local model and return the response."""
        conversation = self.get_or_create_conversation(model_name)
        conversation.add_message("user", query)
        
        # Check if Ollama is running
        if not self.ollama_client.is_ollama_running():
            return "Error: Ollama is not running. Please start Ollama first."
        
        # Check if model is available
        if not self.ollama_client.is_model_available(model_name):
            logger.info(f"Model {model_name} not found, attempting to pull...")
            if not self.ollama_client.pull_model(model_name):
                return f"Error: Failed to load model {model_name}. Please ensure Ollama is running and the model is available."
        
        try:
            # Generate response using local model
            response = self.ollama_client.generate_response(
                model_name=model_name,
                messages=conversation.get_context(),
                max_tokens=1000,
                temperature=0.7
            )
            
            # Add response to conversation
            conversation.add_message("assistant", response)
            return response
                
        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {e}")
            return f"Error: An unexpected error occurred while processing your request: {str(e)}"
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all models."""
        return self.model_manager.get_model_status()
    
    def setup_models(self) -> Dict[str, bool]:
        """Setup all recommended models."""
        return self.model_manager.setup_models()

class JOATSystem:
    """Main system class that orchestrates the entire process."""
    
    def __init__(self, models_mapping_file: str = "models_mapping.txt"):
        self.models_mapping = self.load_models_mapping(models_mapping_file)
        self.task_classifier = TaskClassifier()
        self.model_manager = LocalModelManager(self.models_mapping)
        self.current_model = None
    
    def load_models_mapping(self, file_path: str) -> Dict[str, str]:
        """Load the models mapping from the specified file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                # Parse the simple format: {task: model, task: model}
                content = content.replace('\n', '').replace(' ', '')
                content = content[1:-1]  # Remove outer braces
                
                mapping = {}
                for pair in content.split(','):
                    if ':' in pair:
                        task, model = pair.split(':', 1)
                        mapping[task] = model
                
                logger.info(f"Loaded models mapping: {mapping}")
                return mapping
                
        except FileNotFoundError:
            logger.error(f"Models mapping file not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading models mapping: {e}")
            return {}
    
    def process_query(self, query: str) -> str:
        """Process a user query and return the response."""
        if not query.strip():
            return "Please provide a query."
        
        # If we have a current model and the query seems like a continuation
        if self.current_model and self.is_continuation_query(query):
            # Continue with the current model
            return self.model_manager.send_query(self.current_model, query)
        
        # Classify the task
        task_type = self.task_classifier.classify_task(query)
        logger.info(f"Classified query as task type: {task_type}")
        
        # Get the appropriate model for this task
        model_name = self.models_mapping.get(task_type)
        if not model_name:
            return f"Error: No model configured for task type '{task_type}'"
        
        # Set the current model
        self.current_model = model_name
        logger.info(f"Using model: {model_name} for task: {task_type}")
        
        # Send the query to the model
        return self.model_manager.send_query(model_name, query)
    
    def is_continuation_query(self, query: str) -> bool:
        """Determine if a query is likely a continuation of the current conversation."""
        continuation_indicators = [
            'continue', 'more', 'and', 'also', 'further', 'next', 'what about',
            'how about', 'can you', 'could you', 'please', 'thanks', 'thank you'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in continuation_indicators)
    
    def get_conversation_history(self, model_name: Optional[str] = None) -> List[Dict[str, str]]:
        """Get conversation history for a specific model or all models."""
        if model_name:
            conversation = self.model_manager.conversations.get(model_name)
            return conversation.messages if conversation else []
        else:
            all_messages = []
            for conv in self.model_manager.conversations.values():
                all_messages.extend(conv.messages)
            return all_messages
    
    def clear_conversation(self, model_name: Optional[str] = None):
        """Clear conversation history for a specific model or all models."""
        if model_name:
            if model_name in self.model_manager.conversations:
                del self.model_manager.conversations[model_name]
                if self.current_model == model_name:
                    self.current_model = None
        else:
            self.model_manager.conversations.clear()
            self.current_model = None
    
    def check_ollama_status(self) -> Dict:
        """Check Ollama and model status."""
        return {
            'ollama_running': self.model_manager.ollama_client.is_ollama_running(),
            'models_status': self.model_manager.get_model_status(),
            'available_models': self.model_manager.ollama_client.get_available_models()
        }

def main():
    """Main function to run the JOAT system."""
    print("🤖 JOAT - Just One AI Tool (Local Ollama Edition)")
    print("=" * 60)
    print("I can help you with various tasks using local AI models.")
    print("Type 'quit' to exit, 'history' to see conversation history, 'clear' to clear history.")
    print("Type 'status' to check Ollama and model status.")
    print("=" * 60)
    
    # Initialize the system
    system = JOATSystem()
    
    if not system.models_mapping:
        print("❌ Error: Could not load models mapping. Please check the models_mapping.txt file.")
        return
    
    print(f"✅ Loaded {len(system.models_mapping)} model mappings")
    
    # Check Ollama status
    status = system.check_ollama_status()
    if not status['ollama_running']:
        print("⚠️  Warning: Ollama is not running. Please start Ollama first.")
        print("   Download from: https://ollama.ai/")
        print("   Then run: ollama serve")
    else:
        print("✅ Ollama is running")
        print(f"📦 Available models: {', '.join(status['available_models']) if status['available_models'] else 'None'}")
    
    print()
    
    while True:
        try:
            # Get user input
            query = input("You: ").strip()
            
            if not query:
                continue
            
            # Handle special commands
            if query.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif query.lower() == 'history':
                history = system.get_conversation_history()
                if history:
                    print("\n📜 Conversation History:")
                    for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
                        role = "🤖" if msg["role"] == "assistant" else "👤"
                        print(f"{i}. {role} {msg['content'][:100]}...")
                else:
                    print("📜 No conversation history yet.")
                print()
                continue
            elif query.lower() == 'clear':
                system.clear_conversation()
                print("🗑️ Conversation history cleared.")
                print()
                continue
            elif query.lower() == 'status':
                status = system.check_ollama_status()
                print("\n🔍 System Status:")
                print(f"Ollama Running: {'✅' if status['ollama_running'] else '❌'}")
                print("Model Status:")
                for model, available in status['models_status'].items():
                    print(f"  {model}: {'✅' if available else '❌'}")
                print()
                continue
            
            # Process the query
            print("🤖 Processing...")
            response = system.process_query(query)
            print(f"🤖 {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"❌ An error occurred: {e}")
            print()

if __name__ == "__main__":
    main() 