#!/usr/bin/env python3
"""
JOAT Comprehensive Model Setup
Installs the best specialized open-source models for each task type.
"""

import subprocess
import sys
import time
import requests
from typing import Dict, List, Tuple

class ComprehensiveModelSetup:
    def __init__(self):
        self.models_config = {
            'coding_generation': {
                'model': 'codellama',
                'description': 'Code generation, debugging, programming tasks',
                'size': '~3.8GB',
                'priority': 'high'
            },
            'text_generation': {
                'model': 'llama3',
                'description': 'Creative writing, content generation',
                'size': '~4.7GB',
                'priority': 'high'
            },
            'mathematical_reasoning': {
                'model': 'wizard-math',
                'description': 'Math problems, calculations, equations',
                'size': '~4.1GB',
                'priority': 'high'
            },
            'commonsense_reasoning': {
                'model': 'phi3',
                'description': 'Logical reasoning, explanations, common sense',
                'size': '~2.7GB',
                'priority': 'medium'
            },
            'question_answering': {
                'model': 'mistral',
                'description': 'Factual questions, information retrieval',
                'size': '~4.1GB',
                'priority': 'high'
            },
            'dialogue_systems': {
                'model': 'llama3',
                'description': 'General conversation, chat',
                'size': '~4.7GB',
                'priority': 'high'
            },
            'summarization': {
                'model': 'mixtral',
                'description': 'Text summarization, key point extraction',
                'size': '~26GB',
                'priority': 'low'
            },
            'sentiment_analysis': {
                'model': 'phi3',
                'description': 'Emotion analysis, sentiment detection',
                'size': '~2.7GB',
                'priority': 'medium'
            },
            'visual_question_answering': {
                'model': 'llava',
                'description': 'Image analysis, visual questions',
                'size': '~4.5GB',
                'priority': 'medium'
            },
            'video_question_answering': {
                'model': 'llama3',
                'description': 'Video analysis, motion understanding',
                'size': '~4.7GB',
                'priority': 'low'
            }
        }
    
    def check_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_installed_models(self) -> List[str]:
        """Get list of currently installed models."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama."""
        try:
            print(f"🔄 Pulling {model_name}...")
            result = subprocess.run(
                ['ollama', 'pull', model_name],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            if result.returncode == 0:
                print(f"✅ Successfully pulled {model_name}")
                return True
            else:
                print(f"❌ Failed to pull {model_name}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout while pulling {model_name}")
            return False
        except Exception as e:
            print(f"❌ Error pulling {model_name}: {e}")
            return False
    
    def calculate_total_size(self, models: List[str]) -> str:
        """Calculate approximate total size for selected models."""
        total_gb = 0
        for model in models:
            if model in self.models_config:
                size_str = self.models_config[model]['size']
                try:
                    size_gb = float(size_str.replace('~', '').replace('GB', ''))
                    total_gb += size_gb
                except:
                    pass
        
        if total_gb > 0:
            return f"~{total_gb:.1f}GB"
        return "Unknown"
    
    def show_model_selection(self) -> List[str]:
        """Show model selection interface."""
        print("\n🤖 JOAT Comprehensive Model Setup")
        print("=" * 60)
        print("This will install the best specialized models for each task type.")
        print("Models are ranked by priority and specialization.")
        print()
        
        # Show current models
        installed_models = self.get_installed_models()
        print("📦 Currently installed models:")
        if installed_models:
            for model in installed_models:
                print(f"   ✅ {model}")
        else:
            print("   None")
        print()
        
        # Show recommended models by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for task, config in self.models_config.items():
            model = config['model']
            if model not in installed_models:
                if config['priority'] == 'high':
                    high_priority.append((task, config))
                elif config['priority'] == 'medium':
                    medium_priority.append((task, config))
                else:
                    low_priority.append((task, config))
        
        print("🎯 Recommended Installation Order:")
        print()
        
        if high_priority:
            print("🔥 HIGH PRIORITY (Essential for core functionality):")
            for task, config in high_priority:
                print(f"   • {config['model']} ({config['size']}) - {config['description']}")
            print()
        
        if medium_priority:
            print("⚡ MEDIUM PRIORITY (Specialized capabilities):")
            for task, config in medium_priority:
                print(f"   • {config['model']} ({config['size']}) - {config['description']}")
            print()
        
        if low_priority:
            print("💡 LOW PRIORITY (Advanced features):")
            for task, config in low_priority:
                print(f"   • {config['model']} ({config['size']}) - {config['description']}")
            print()
        
        # Calculate sizes
        all_missing = [config['model'] for _, config in high_priority + medium_priority + low_priority]
        total_size = self.calculate_total_size(all_missing)
        
        print(f"📊 Total download size: {total_size}")
        print()
        
        # Get user choice
        print("Choose installation option:")
        print("1. Install HIGH PRIORITY only (recommended for first time)")
        print("2. Install HIGH + MEDIUM priority")
        print("3. Install ALL models (full experience)")
        print("4. Custom selection")
        print("5. Skip installation")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                if choice == '1':
                    return [config['model'] for _, config in high_priority]
                elif choice == '2':
                    return [config['model'] for _, config in high_priority + medium_priority]
                elif choice == '3':
                    return [config['model'] for _, config in high_priority + medium_priority + low_priority]
                elif choice == '4':
                    return self.custom_selection(high_priority + medium_priority + low_priority)
                elif choice == '5':
                    return []
                else:
                    print("Please enter a number between 1-5")
            except KeyboardInterrupt:
                print("\n\nInstallation cancelled.")
                return []
    
    def custom_selection(self, all_models: List[Tuple[str, Dict]]) -> List[str]:
        """Allow custom model selection."""
        print("\n🎛️ Custom Model Selection:")
        print("Enter the numbers of models you want to install (comma-separated):")
        
        for i, (task, config) in enumerate(all_models, 1):
            print(f"{i}. {config['model']} ({config['size']}) - {config['description']}")
        
        try:
            selection = input("\nEnter model numbers (e.g., 1,3,5): ").strip()
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_models = []
            
            for idx in indices:
                if 0 <= idx < len(all_models):
                    selected_models.append(all_models[idx][1]['model'])
            
            return selected_models
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")
            return self.custom_selection(all_models)
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled.")
            return []
    
    def install_models(self, models: List[str]) -> Dict[str, bool]:
        """Install the selected models."""
        if not models:
            print("No models selected for installation.")
            return {}
        
        print(f"\n🚀 Installing {len(models)} models...")
        print("This may take a while depending on your internet connection.")
        print()
        
        results = {}
        for i, model in enumerate(models, 1):
            print(f"📦 [{i}/{len(models)}] Installing {model}...")
            success = self.pull_model(model)
            results[model] = success
            
            if i < len(models):
                print("⏳ Waiting 5 seconds before next model...")
                time.sleep(5)
        
        return results
    
    def show_results(self, results: Dict[str, bool]):
        """Show installation results."""
        print("\n📊 Installation Results:")
        print("=" * 40)
        
        successful = [model for model, success in results.items() if success]
        failed = [model for model, success in results.items() if not success]
        
        if successful:
            print("✅ Successfully installed:")
            for model in successful:
                print(f"   • {model}")
        
        if failed:
            print("\n❌ Failed to install:")
            for model in failed:
                print(f"   • {model}")
            print("\n💡 You can try installing failed models manually:")
            for model in failed:
                print(f"   ollama pull {model}")
        
        print(f"\n🎉 Installation complete! {len(successful)}/{len(results)} models installed.")
    
    def run(self):
        """Run the comprehensive setup."""
        print("🔍 Checking Ollama status...")
        
        if not self.check_ollama_running():
            print("❌ Ollama is not running!")
            print("Please start Ollama first:")
            print("   brew services start ollama  # macOS")
            print("   ollama serve               # Other platforms")
            return
        
        print("✅ Ollama is running")
        
        # Show model selection
        selected_models = self.show_model_selection()
        
        if not selected_models:
            print("No models selected. Setup complete.")
            return
        
        # Install models
        results = self.install_models(selected_models)
        
        # Show results
        self.show_results(results)
        
        print("\n🎯 Next steps:")
        print("1. Run the GUI: python gui_app.py")
        print("2. Run the CLI: python main.py")
        print("3. Test with: python example.py")

        print("\n[INFO] Some models (like 'llama3') are used for both essential and advanced tasks. The priority refers to the *task*, not the model. If you install only high-priority models, you will still be able to use advanced tasks, but with generalist models.\n")

def main():
    """Main function."""
    setup = ComprehensiveModelSetup()
    setup.run()

if __name__ == "__main__":
    main() 