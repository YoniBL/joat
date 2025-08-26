#!/usr/bin/env python3
"""
JOAT Profile Model Setup (small or regular)
Installs models for the selected profile defined in models_mapping.json.
"""

import subprocess
import sys
import time
import requests
import os
from typing import Dict, List, Tuple
import json

def load_models_from_mapping(mapping_file="models_mapping.json", profile_key: str = "regular_sized_models"):
    """Load model-task mapping from JSON and return a dict of {task: model}."""
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

class ComprehensiveModelSetup:
    def __init__(self):
        # Load from mapping file (both profiles)
        mapping_path = os.path.join(os.path.dirname(__file__), 'models_mapping.json')
        with open(mapping_path, 'r') as f:
            data = json.load(f)
        self.profiles = {
            'small_sized_models': data.get('small_sized_models', {}),
            'regular_sized_models': data.get('regular_sized_models', {})
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
        """Show profile selection and return list of models for that profile."""
        print("\n🤖 JOAT Model Profile Setup")
        print("=" * 60)
        print("Select which profile to install:")
        print("1. small_sized_models (fast and lightweight)")
        print("2. regular_sized_models (higher quality)")
        while True:
            try:
                choice = input("\nEnter your choice (1-2): ").strip()
                if choice == '1':
                    profile_key = 'small_sized_models'
                    break
                elif choice == '2':
                    profile_key = 'regular_sized_models'
                    break
                else:
                    print("Please enter 1 or 2")
            except KeyboardInterrupt:
                print("\n\nInstallation cancelled.")
                return []
        models = list(self.profiles.get(profile_key, {}).values())
        print(f"\nSelected profile: {profile_key}")
        if models:
            print("Models to install:")
            for m in models:
                print(f"   • {m}")
        else:
            print("No models configured for this profile.")
        return models
    
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

        print("\n[INFO] You can switch profiles later by setting JOAT_PROFILE=small_sized_models or regular_sized_models.\n")

def main():
    """Main function."""
    setup = ComprehensiveModelSetup()
    setup.run()

if __name__ == "__main__":
    main() 