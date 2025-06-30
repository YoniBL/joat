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
python gui_app.py
# or
python app_launcher.py
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
| `summarization` | **mixtral** | Text summarization, key point extraction | ~26GB | 💡 Low |
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
- **mistral**: Strong general knowledge and Q&A
- **mixtral**: Advanced summarization capabilities
- **llava**: Visual understanding and image analysis

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
- `llama3` - Text generation & dialogue
- `wizard-math` - Mathematical reasoning
- `mistral` - Question answering

**⚡ Medium Priority (Enhanced - +12GB):**
- `phi3` - Commonsense & sentiment analysis
- `llava` - Visual question answering

**💡 Low Priority (Advanced - +30GB):**
- `mixtral` - Advanced summarization

## 🎯 **Usage Examples**

### **Desktop GUI**
1. Launch: `python gui_app.py`
2. Type your query in the input box
3. Press Enter or click Send
4. Watch the AI route your query to the best model
5. See which model was used in the response

### **Command Line**
```bash
python main.py

You: Write a Python function to calculate fibonacci numbers
🤖 [Response from codellama]

You: Solve the equation 2x + 5 = 13
🤖 [Response from wizard-math]

You: What is the capital of France?
🤖 [Response from llama3]
```

## 🔧 **Configuration**

### **Models Mapping**
Edit `models_mapping.txt` to customize which models handle which tasks:

```
{coding_generation: codellama,
text_generation: llama3,
mathematical_reasoning: wizard-math,
...}
```

### **Adding New Models**
1. Install the model: `ollama pull your-model`
2. Add to `models_mapping.txt`
3. Restart the app

## 🛠️ **Troubleshooting**

### **Ollama Issues**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
brew services restart ollama

# Check Ollama logs
brew services info ollama
```

### **Model Issues**
```bash
# List installed models
ollama list

# Remove a model
ollama rm model-name

# Pull a model again
ollama pull model-name
```

### **GUI Issues**
- Make sure you have tkinter: `python -c "import tkinter"`
- On macOS, tkinter is usually included with Python
- On Linux: `sudo apt-get install python3-tk`

## 📁 **File Structure**

```
joat/
├── main.py              # CLI version
├── gui_app.py           # Desktop GUI version
├── app_launcher.py      # GUI launcher with checks
├── ollama_client.py     # Ollama API client
├── setup_ollama.py      # Model setup script
├── models_mapping.txt   # Task-to-model mapping
├── requirements.txt     # Python dependencies
├── LOCAL_SETUP.md       # Detailed local setup guide
└── README.md           # This file
```

## 🎨 **GUI Features**

- **Modern Design**: Clean, modern chat-like interface
- **Real-time Status**: Live Ollama and model status
- **Model Information**: Shows which models are available
- **Conversation History**: Maintains chat history
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **Responsive Layout**: Adapts to window size
- **Error Handling**: Graceful error messages

## 🔄 **Conversation Management**

### **In GUI:**
- Click "🗑️ Clear History" to clear all conversations
- Each model maintains its own conversation context
- Automatic model switching based on task type

### **In CLI:**
- Type `clear` to clear history
- Type `history` to see conversation history
- Type `status` to check system status
- Type `quit` to exit

## 📈 **Performance Tips**

1. **SSD Storage**: Models load faster from SSD
2. **RAM**: 8GB+ recommended for smooth operation
3. **GPU**: Optional but speeds up inference
4. **Model Selection**: Use smaller models for faster responses

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

[Add your license information here]

---

**Enjoy your local AI assistant! 🤖✨** 
