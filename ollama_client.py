#!/usr/bin/env python3
"""
Ollama Client for JOAT
Handles communication with local Ollama models.
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with local Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama not running: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available, accepting both with and without :latest tag."""
        available_models = self.get_available_models()
        # Accept model_name, model_name:latest, and model_name without tag as equivalent
        candidates = {model_name}
        if ':' not in model_name:
            candidates.add(f"{model_name}:latest")
        elif model_name.endswith(":latest"):
            candidates.add(model_name.split(":")[0])
        return any(candidate in available_models for candidate in candidates)
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama library."""
        try:
            logger.info(f"Pulling model: {model_name}")
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def generate_response(self, model_name: str, messages: List[Dict[str, str]], 
                         max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate a response using the specified model."""
        try:
            # Convert messages to Ollama format
            prompt = self._format_messages_for_ollama(messages)
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            logger.info(f"Generating response with model: {model_name}")
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # Longer timeout for local models
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Error generating response: {response.status_code}")
                return f"Error: Failed to generate response (Status: {response.status_code})"
                
        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {e}")
            return f"Error: {str(e)}"
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages for Ollama prompt."""
        formatted_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'user':
                formatted_messages.append(f"User: {content}")
            elif role == 'assistant':
                formatted_messages.append(f"Assistant: {content}")
        
        # Add the final user message if it exists
        if messages and messages[-1].get('role') == 'user':
            return '\n'.join(formatted_messages)
        else:
            return '\n'.join(formatted_messages) + '\nAssistant:'
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get information about a specific model."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}

def load_models_from_mapping(mapping_file: str = "models_mapping.json", profile_key: str = "regular_sized_models"):
    """Load model-task mapping from JSON file and return a dict of {task: model}."""
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

class OllamaModelManager:
    """Manages Ollama models for different task types."""
    
    def __init__(self):
        self.client = OllamaClient()
        # Recommended models: union of small and regular profiles from JSON
        try:
            data = {}
            mapping_path = os.path.join(os.path.dirname(__file__), 'models_mapping.json')
            with open(mapping_path, 'r') as f:
                data = json.load(f)
            regular = data.get('regular_sized_models', {})
            small = data.get('small_sized_models', {})
            self.recommended_models = sorted(list(set(list(regular.values()) + list(small.values()))))
        except Exception:
            self.recommended_models = []
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available, pull if necessary."""
        if self.client.is_model_available(model_name):
            return True
        
        logger.info(f"Model {model_name} not found, attempting to pull...")
        return self.client.pull_model(model_name)
    
    def get_recommended_models(self) -> List[str]:
        """Get list of recommended models to install."""
        return self.recommended_models
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all recommended models."""
        status = {}
        for model_name in self.recommended_models:
            status[model_name] = self.client.is_model_available(model_name)
        return status
    
    def setup_models(self) -> Dict[str, bool]:
        """Setup all recommended models."""
        results = {}
        for model_name in self.recommended_models:
            logger.info(f"Setting up model: {model_name}")
            results[model_name] = self.ensure_model_available(model_name)
        return results 