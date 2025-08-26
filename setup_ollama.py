#!/usr/bin/env python3
"""
Ollama Setup Script for JOAT
Helps users install and configure Ollama models for local AI processing.
"""

import subprocess
import sys
import os
import time
from ollama_client import OllamaModelManager
import json

def check_ollama_installation():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def install_ollama():
    """Install Ollama if not already installed."""
    print("📦 Installing Ollama...")
    
    system = sys.platform
    if system == "darwin":  # macOS
        print("Installing Ollama on macOS...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    elif system.startswith("linux"):
        print("Installing Ollama on Linux...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    elif system == "win32":
        print("Installing Ollama on Windows...")
        print("Please download and install Ollama from: https://ollama.ai/download")
        return False
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def start_ollama():
    """Start Ollama service."""
    print("🚀 Starting Ollama service...")
    
    try:
        # Check if Ollama is already running
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is already running")
            return True
    except:
        pass
    
    try:
        # Start Ollama in background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for Ollama to start
        print("⏳ Waiting for Ollama to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            try:
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✅ Ollama started successfully!")
                    return True
            except:
                pass
        
        print("❌ Ollama failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def setup_models():
    """Setup models for the default comprehensive (regular) profile."""
    print("\n📦 Installing default model profile: regular_sized_models")
    mapping_path = os.path.join(os.path.dirname(__file__), 'models_mapping.json')
    try:
        with open(mapping_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load mapping: {e}")
        return

    profile_key = 'regular_sized_models'
    profile_models = list((data.get(profile_key) or {}).values())
    if not profile_models:
        print("❌ No models found in regular_sized_models profile")
        return

    print(f"Models to install: {', '.join(profile_models)}")
    print("This will download data. Continue? (y/n): ", end="")
    response = input().lower().strip()
    if response != 'y':
        print("⏭️  Skipping model setup")
        return

    manager = OllamaModelManager()
    # override recommended_models during this run to chosen profile
    manager.recommended_models = profile_models
    print("\n🔄 Setting up models (this may take a while)...")
    results = manager.setup_models()
    print("\n📊 Setup Results:")
    for model, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {model}")
    successful_models = [model for model, success in results.items() if success]
    if successful_models:
        print(f"\n🎉 Successfully set up {len(successful_models)} models!")
        print(f"Ready models: {', '.join(successful_models)}")
    else:
        print("\n❌ No models were set up successfully")

def main():
    """Main setup function."""
    print("🚀 JOAT Ollama Setup")
    print("=" * 50)
    print("This script will help you set up Ollama for local AI processing.")
    print()
    
    # Check if Ollama is installed
    if not check_ollama_installation():
        print("\n📦 Ollama Installation Required")
        print("=" * 30)
        print("Ollama is not installed. Would you like to install it now? (y/n): ", end="")
        
        response = input().lower().strip()
        if response == 'y':
            if not install_ollama():
                print("\n❌ Failed to install Ollama automatically.")
                print("Please install Ollama manually from: https://ollama.ai/")
                return
        else:
            print("⏭️  Skipping Ollama installation")
            print("Please install Ollama manually from: https://ollama.ai/")
            return
    
    # Start Ollama
    if not start_ollama():
        print("\n❌ Failed to start Ollama.")
        print("Please start Ollama manually by running: ollama serve")
        return
    
    # Setup models
    setup_models()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nYou can now run JOAT with:")
    print("  python main.py")
    print("\nOr test the system with:")
    print("  python example.py")

if __name__ == "__main__":
    main() 