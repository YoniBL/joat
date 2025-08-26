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
        self.ollama_client = OllamaClient()
        self.model_manager = OllamaModelManager()
        
        # Check if Ollama is running
        if not self.ollama_client.is_ollama_running():
            logger.warning("Ollama is not running. Please start Ollama first.")
    
    def send_query(self, model_name: str, query: str, history: List[Dict[str, str]]) -> str:
        """Send a query to the specified local model and return the response."""
        messages = history + [{"role": "user", "content": query}]
        
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
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # The client will manage conversation history
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

def load_models_from_mapping(mapping_file="models_mapping.txt"):
    """Load model-task mapping from file and return a dict of {task: model}."""
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    with open(mapping_file, "r") as f:
        content = f.read().strip().replace('\n', '').replace(' ', '')
        content = content[1:-1]  # Remove outer braces
        mapping = {}
        for pair in content.split(','):
            if ':' in pair:
                task, model = pair.split(':', 1)
                mapping[task] = model
        return mapping

class JOATSystem:
    """Main system class that orchestrates the entire process."""
    
    def __init__(self, models_mapping_file: str = "models_mapping.txt", essential_mode: bool = False):
        self.models_mapping = self.load_models_mapping(models_mapping_file)
        self.task_classifier = TaskClassifier()
        self.model_manager = LocalModelManager(self.models_mapping)
        self.essential_mode = essential_mode
        # Modular: Use mapping for fallbacks and high-priority models
        mapping = load_models_from_mapping(models_mapping_file)
        # Default high-priority models (can be extended or made configurable)
        default_high_priority = {'deepseek-coder', 'llama3.1', 'deepseek-r1:8b', 'mistral', 'qwen3'}
        self.high_priority_fallbacks = {task: model for task, model in mapping.items() if model in default_high_priority}
        self.high_priority_models = set(model for model in mapping.values() if model in default_high_priority)
    
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
    
    def process_query(self, query: str, history: List[Dict[str, str]] = None) -> Dict:
        """Process a user query and return the response."""
        if history is None:
            history = []
        if not query.strip():
            return {"response": "Please provide a query.", "task_type": "error", "model_used": None}
        
        # Classify the task
        task_type = self.task_classifier.classify_task(query)
        logger.info(f"Classified query as task type: {task_type}")
        
        # Get the appropriate model for this task
        model_name = self.models_mapping.get(task_type)
        used_fallback = False
        fallback_reason = None
        
        if self.essential_mode:
            # If the mapped model is not high-priority, fallback if possible
            if model_name not in self.high_priority_models:
                fallback_model = self.high_priority_fallbacks.get(task_type)
                if fallback_model and fallback_model in self.high_priority_models:
                    used_fallback = True
                    fallback_reason = f"Essential mode: Falling back from '{model_name}' to high-priority model '{fallback_model}' for task '{task_type}'."
                    model_name = fallback_model
                else:
                    return {
                        "response": f"Essential mode: No high-priority model available for task type '{task_type}'. Please install a suitable model or disable essential mode.",
                        "task_type": task_type,
                        "model_used": None
                    }
        if not model_name:
            return {
                "response": f"Error: No model configured for task type '{task_type}'",
                "task_type": task_type,
                "model_used": None
            }
        logger.info(f"Using model: {model_name} for task: {task_type}")
        # Send the query to the model
        response = self.model_manager.send_query(model_name, query, history)
        if used_fallback and fallback_reason:
            response = f"[INFO] {fallback_reason}\n{response}"
        return {
            "response": response,
            "task_type": task_type,
            "model_used": model_name
        }
    
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
    
    history = []
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
                if history:
                    print("\n📜 Conversation History:")
                    for i, msg in enumerate(history[-20:], 1):  # Show last 20 messages
                        role = "🤖" if msg["role"] == "assistant" else "👤"
                        print(f"{i}. {role} {msg['content'][:100]}...")
                else:
                    print("📜 No conversation history yet.")
                print()
                continue
            elif query.lower() == 'clear':
                history = []
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
            user_message = {"role": "user", "content": query}
            
            response_data = system.process_query(query, history)
            response = response_data["response"]
            
            print(f"🤖 {response}")
            
            history.append(user_message)
            history.append({"role": "assistant", "content": response})
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