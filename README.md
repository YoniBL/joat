# JOAT - Just One AI Tool

A multi-model conversation system that intelligently routes user queries to specialized AI models based on task type, maintaining conversation context for each model. Now with **local Ollama models** and a **beautiful desktop GUI**!

## Features

- **Intelligent Task Classification**: Automatically classifies user queries into different task types
- **Multi-Model Routing**: Routes queries to the most appropriate AI model for each task
- **Conversation Context**: Maintains separate conversation histories for each model
- **Local AI Models**: Uses Ollama for cost-effective local AI processing
- **Beautiful Desktop GUI**: Modern chat interface inspired by leading chat apps
- **Command Line Interface**: Traditional CLI for power users
- **Easy Setup**: Simple installation and configuration

## 🖥️ **Desktop GUI vs Command Line**

### **Desktop GUI (Recommended)**
```bash
# On any OS (macOS, Windows, Linux)
python gui_app.py

# Or on macOS/Linux
./start_gui.sh
```

**Features:**
- 🎨 Beautiful modern interface
- 💬 Real-time chat experience
- 📊 Live model status display
- 🗑️ Easy conversation management
- ⌨️ Enter to send, Shift+Enter for new line

### **Command Line Interface**
```bash
python main.py
```

**Features:**
- ⚡ Fast and lightweight
- 🔧 Full control and debugging
- 📝 Scriptable and automatable
- 🖥️ Works on any terminal

## Supported Task Types

| Task Type | Model | Description | Size | Priority |
|-----------|-------|-------------|------|----------|
| `coding_generation` | **codellama** | Code generation, debugging, programming tasks | ~3.8GB | 🔥 High |
| `text_generation` | **llama3** | Creative writing, content generation | ~4.7GB | 🔥 High |
| `mathematical_reasoning` | **wizard-math** | Math problems, calculations, equations | ~4.1GB | 🔥 High |
| `commonsense_reasoning` | **phi3** | Logical reasoning, explanations, common sense | ~2.7GB | ⚡ Medium |
| `question_answering` | **mistral** | Factual questions, information retrieval | ~4.1GB | 🔥 High |
| `dialogue_systems` | **llama3** | General conversation, chat | ~4.7GB | 🔥 High |
| `summarization` (advanced) | **mixtral** | Advanced summarization, key point extraction | ~26GB | 💡 Low |
| `summarization` (essential) | **mistral** | Fast summarization (smaller model) | ~4.1GB | ⚡ Medium |
| `sentiment_analysis` | **phi3** | Emotion analysis, sentiment detection | ~2.7GB | ⚡ Medium |
| `visual_question_answering` | **llava** | Image analysis, visual questions | ~4.5GB | ⚡ Medium |
| `video_question_answering` | **llama3** | Video analysis, motion understanding | ~4.7GB | 💡 Low |

**Why This Model Selection?**

- **🔥 High Priority**: Essential models for core functionality
- **⚡ Medium Priority**: Specialized models for enhanced capabilities  
- **💡 Low Priority**: Advanced features for power users

Each model is carefully chosen for its specialization:
- **codellama**: Best-in-class code generation
- **wizard-math**: Specialized for mathematical reasoning
- **phi3**: Excellent for commonsense and sentiment analysis
- **mistral**: Strong general knowledge, Q&A, and fast summarization
- **mixtral**: Advanced summarization capabilities (large model)
- **llava**: Visual understanding and image analysis

**Note:** Some models (such as `llama3`) are used for both essential and advanced tasks. The priority listed in this table refers to the *task*, not the model. If you install only high-priority models, you will still be able to use advanced features, but with generalist models.

## 🚀 Quick Start

### 1. **Install Ollama**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/
```

### 2. **Start Ollama**
```bash
brew services start ollama  # macOS
# or
ollama serve               # Any platform
```

### 3. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Install AI Models** (Optional - will auto-download when needed)
```bash
python setup_ollama.py
```

### 5. **Launch the App**

**Desktop GUI (Recommended):**
```bash
python gui_app.py
# or on macOS/Linux
./start_gui.sh
```

**Command Line:**
```bash
python main.py
```

## 📦 **Model Installation**

The app will automatically download models as needed, but you can pre-install them:

### **Comprehensive Setup (Recommended)**
```bash
# Install the best specialized models for each task
python setup_comprehensive_models.py
```

This script will:
- Show you which models are recommended for each task type
- Let you choose installation priority (High/Medium/Low)
- Calculate total download size
- Install models with progress tracking

### **Manual Installation**
```bash
# Install all recommended models
python setup_ollama.py

# Or install individually
ollama pull llama3
ollama pull codellama
ollama pull wizard-math
ollama pull phi3
ollama pull mistral
ollama pull mixtral
ollama pull llava
```

### **Installation Options**

**🔥 High Priority (Essential - ~17GB total):**
- `codellama` - Code generation
- `llama3` - Text generation & dialogue (also used for advanced tasks like video QA)
- `wizard-math` - Mathematical reasoning
- `mistral` - Question answering & essential summarization

**⚡ Medium Priority (Enhanced - +12GB):**
- `phi3` - Commonsense & sentiment analysis
- `llava` - Visual question answering

**💡 Low Priority (Advanced - +30GB):**
- `mixtral` - Advanced summarization (large model)

> **Note:** Some models (like `llama3`) are used for both essential and advanced tasks. The priority refers to the *task*, not the model. If you install only high-priority models, you will still be able to use advanced features, but with generalist models.

## 🎯 **Usage Examples**

### **Desktop GUI**
1. Launch: `python gui_app.py`