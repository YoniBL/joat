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
        """Check if a specific model is available."""
        available_models = self.get_available_models()
        return model_name in available_models
    
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

class OllamaModelManager:
    """Manages Ollama models for different task types."""
    
    def __init__(self):
        self.client = OllamaClient()
        self.model_configs = {
            'codellama': {
                'description': 'Code generation and programming tasks',
                'size': '~4GB',
                'tags': ['coding', 'programming', 'development']
            },
            'llama3': {
                'description': 'General purpose text generation and reasoning',
                'size': '~4GB',
                'tags': ['general', 'text', 'reasoning']
            },
            'wizard-math': {
                'description': 'Mathematical reasoning and problem solving',
                'size': '~4GB',
                'tags': ['math', 'reasoning', 'problem-solving']
            },
            'llava': {
                'description': 'Visual question answering and image analysis',
                'size': '~4GB',
                'tags': ['vision', 'image', 'visual']
            }
        }
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available, pull if necessary."""
        if self.client.is_model_available(model_name):
            return True
        
        logger.info(f"Model {model_name} not found, attempting to pull...")
        return self.client.pull_model(model_name)
    
    def get_recommended_models(self) -> List[str]:
        """Get list of recommended models to install."""
        return list(self.model_configs.keys())
    
    def get_model_status(self) -> Dict[str, bool]:
        """Get status of all recommended models."""
        status = {}
        for model_name in self.model_configs.keys():
            status[model_name] = self.client.is_model_available(model_name)
        return status
    
    def setup_models(self) -> Dict[str, bool]:
        """Setup all recommended models."""
        results = {}
        for model_name in self.model_configs.keys():
            logger.info(f"Setting up model: {model_name}")
            results[model_name] = self.ensure_model_available(model_name)
        return results 