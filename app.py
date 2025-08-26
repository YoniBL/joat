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
        # Math vs coding pattern indicators
        self.math_indicators = {
            'strong': [
                r'\b\d+\s*[\+\-\*/\^]\s*\d+',  # Mathematical expressions
                r'\b(?:sin|cos|tan|log|ln|sqrt|integral|derivative)\b',  # Math functions
                r'\b(?:equation|formula|theorem|proof|algebra|calculus|geometry|statistics)\b',
                r'\b(?:solve for [a-z]|find [a-z]|what is [a-z])\b',  # Math problem patterns
                r'\b(?:degrees|radians|percentage|probability)\b',
                r'[=<>≤≥≠±∞π∑∏∫]',  # Mathematical symbols
            ],
            'medium': [
                r'\b(?:calculate|compute|evaluate|simplify|factor)\b',
                r'\b(?:number|value|result|answer)\s+(?:of|is|equals)\b',
                r'\b(?:math|mathematics|mathematical)\b',
            ]
        }
        
        self.coding_indicators = {
            'strong': [
                r'\b(?:def|class|import|from|return|if|else|elif|for|while|try|except)\b',  # Python keywords
                r'\b(?:function|variable|array|object|string|boolean|integer)\b',
                r'\b(?:debug|compile|run|execute|script|program|code)\b',
                r'\b(?:API|database|server|client|web|framework)\b',
                r'[\{\}\[\]();<>].*[\{\}\[\]();]',  # Code-like syntax
                r'\b(?:\.py|\.js|\.java|\.cpp|\.html|\.css)\b',  # File extensions
            ],
            'medium': [
                r'\b(?:algorithm|data structure|loop|recursion|iteration)\b',
                r'\b(?:implement|develop|build|create)\s+(?:a|an|the)?\s*(?:program|function|class|script)\b',
                r'\b(?:programming|coding|software|development)\b',
            ]
        }
        
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
    
    def _calculate_pattern_score(self, query: str, patterns: Dict[str, List[str]]) -> float:
        """Calculate weighted pattern matching score."""
        score = 0.0
        query_lower = query.lower()
        
        for weight_name, pattern_list in patterns.items():
            weight = 3.0 if weight_name == 'strong' else 1.5
            
            for pattern in pattern_list:
                matches = len(re.findall(pattern, query_lower))
                score += matches * weight
        
        return score
    
    def _is_math_vs_coding(self, query: str) -> Tuple[Optional[str], float]:
        """Specialized function to distinguish math from coding tasks."""
        math_score = self._calculate_pattern_score(query, self.math_indicators)
        coding_score = self._calculate_pattern_score(query, self.coding_indicators)
        
        query_lower = query.lower()
        
        # Additional context clues
        if any(word in query_lower for word in ['equation', 'derivative', 'integral', 'theorem']):
            math_score += 2.0
        
        if any(word in query_lower for word in ['function', 'class', 'import', 'debug']):
            coding_score += 2.0
        
        # Contextual disambiguation for "solve"
        if 'solve' in query_lower:
            if any(term in query_lower for term in ['for x', 'for y', 'equation', 'formula']):
                math_score += 1.5
            elif any(term in query_lower for term in ['problem', 'challenge', 'leetcode', 'algorithm']):
                coding_score += 1.5
        
        confidence = abs(math_score - coding_score) / max(math_score + coding_score, 1.0)
        
        if math_score > coding_score:
            return 'mathematical_reasoning', confidence
        elif coding_score > math_score:
            return 'coding_generation', confidence
        else:
            return None, 0.0
    
    def classify_task(self, query: str) -> str:
        """Classify the user query into a task type."""
        query_lower = query.lower()
        
        # First, try to distinguish math vs coding specifically
        ambiguous_terms = ['solve', 'algorithm', 'problem', 'calculate', 'compute']
        if any(term in query_lower for term in ambiguous_terms):
            task, confidence = self._is_math_vs_coding(query)
            if task and confidence > 0.3:
                return task
        
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

def load_models_from_mapping(mapping_file: str = "models_mapping.json", profile_key: str = "regular_sized_models") -> Dict[str, str]:
    """Load model-task mapping from JSON file by profile and return a dict of {task: model}."""
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    with open(mapping_file, "r") as f:
        data = json.load(f)
        if profile_key not in data:
            raise KeyError(f"Profile '{profile_key}' not found in {mapping_file}")
        profile_mapping = data[profile_key]
        if not isinstance(profile_mapping, dict):
            raise ValueError("Invalid mapping format: profile must be an object of task→model pairs")
        return profile_mapping

class JOATSystem:
    """Main system class that orchestrates the entire process."""
    
    def __init__(self, models_mapping_file: str = "models_mapping.json", profile_key: str = None, essential_mode: bool = False):
        # Determine active profile: explicit arg, env var, or auto-detect based on installed models
        env_profile = os.getenv("JOAT_PROFILE", "").strip()
        self.profile_key = profile_key or (env_profile if env_profile in {"small_sized_models", "regular_sized_models"} else None)
        if not self.profile_key:
            # Auto-detect profile: choose regular ONLY if all regular models are installed; otherwise choose small
            try:
                mapping_path = os.path.join(os.path.dirname(__file__), 'models_mapping.json')
                with open(mapping_path, 'r') as f:
                    data = json.load(f)
                small_models = set((data.get('small_sized_models') or {}).values())
                regular_models = set((data.get('regular_sized_models') or {}).values())
                available = set(OllamaClient().get_available_models())
                def is_model_installed(model_name: str) -> bool:
                    name_no_tag = model_name.split(':')[0]
                    return any(
                        a == model_name or a == f"{model_name}:latest" or a.split(':')[0] == name_no_tag
                        for a in available
                    )
                all_regular_installed = all(is_model_installed(m) for m in regular_models) if regular_models else False
                self.profile_key = 'regular_sized_models' if all_regular_installed else 'small_sized_models'
            except Exception:
                self.profile_key = 'regular_sized_models'
        self.models_mapping = self.load_models_mapping(models_mapping_file, self.profile_key)
        self.task_classifier = TaskClassifier()
        self.model_manager = LocalModelManager(self.models_mapping)
        self.essential_mode = essential_mode
        # High-priority concept simplified: consider active profile models as the set
        self.high_priority_fallbacks = {}
        self.high_priority_models = set(self.models_mapping.values())
    
    def load_models_mapping(self, file_path: str, profile_key: str) -> Dict[str, str]:
        """Load the models mapping from the specified JSON file and profile."""
        try:
            mapping = load_models_from_mapping(file_path, profile_key)
            logger.info(f"Loaded models mapping for profile '{profile_key}': {mapping}")
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
        print("❌ Error: Could not load models mapping. Please check the models_mapping.json file.")
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
        print(f"🧩 Active profile: {system.profile_key}")
    
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