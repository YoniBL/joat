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

## Supported Task Types and Models

JOAT uses a single comprehensive installation by default (regular profile). You can optionally switch to a small profile for lower resource usage. The mapping lives in `models_mapping.json`.

Regular profile models:
- coding_generation: yi-coder:9b
- text_generation: mistral:7b-instruct
- mathematical_reasoning: qwen2-math:7b
- commonsense_reasoning: mistral:7b-instruct
- question_answering: llama3-chatqa:8b
- dialogue_systems: qwen2.5:7b-instruct
- summarization: llama3.2:3b-instruct
- sentiment_analysis: llama3.1:8b-chat
- visual_question_answering: llava:7b
- video_question_answering: qwen2.5vl:7b

Small profile models (optional):
- coding_generation: deepseek-coder:1.3b
- text_generation: llama3.2:1b
- mathematical_reasoning: deepscaler:1.5b
- commonsense_reasoning: tinyllama:1.1b
- question_answering: phi3.5:3.8b
- dialogue_systems: qwen2.5:3b-instruct
- summarization: phi3.5:3.8b
- sentiment_analysis: llama3.2:1b
- visual_question_answering: moondream:1.8b
- video_question_answering: qwen2.5vl:3b

Each model in the profiles is selected to specialize per task (coding, math, QA, etc.), balancing quality and performance. You can switch profiles at runtime if needed.

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

### 4. **Install AI Models** (Default: Comprehensive)
```bash
python setup_comprehensive_models.py
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

### **Install Models**
```bash
# Default comprehensive (regular profile) interactive installer
python setup_comprehensive_models.py

# Optional minimal one-shot installer (installs regular profile without prompting)
python setup_ollama.py
```

### **Manual Installation**
```bash
# Pull any model from the mapping manually
ollama pull yi-coder:9b
ollama pull qwen2.5:7b-instruct
... # etc.
```

### **Profiles**

- small_sized_models: optimized for speed and low memory.
- regular_sized_models: balanced quality and performance (default install).

## 🎯 **Usage Examples**

### **Desktop GUI**
1. Launch: `python gui_app.py` (or `./start_gui.sh` on macOS/Linux)
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

### **Models Mapping Format**
Edit `models_mapping.json` to customize which models handle which tasks per profile:

```json
{
  "regular_sized_models": {
    "coding_generation": "yi-coder:9b",
    "text_generation": "mistral:7b-instruct",
    "mathematical_reasoning": "qwen2-math:7b",
    "commonsense_reasoning": "mistral:7b-instruct",
    "question_answering": "llama3-chatqa:8b",
    "dialogue_systems": "qwen2.5:7b-instruct",
    "summarization": "llama3.2:8b-instruct",
    "sentiment_analysis": "llama3.1:8b-chat",
    "visual_question_answering": "llava:7b",
    "video_question_answering": "qwen2-vl:7b-instruct"
  },
  "small_sized_models": {
    "coding_generation": "stablecode:3b",
    "text_generation": "llama3.2:1b",
    "mathematical_reasoning": "deepscaler:1.5b",
    "commonsense_reasoning": "tinyllama:1.1b",
    "question_answering": "phi3.5:3.8b",
    "dialogue_systems": "qwen2.5:3b-instruct",
    "summarization": "phi3.5:3.8b",
    "sentiment_analysis": "llama3.2:1b",
    "visual_question_answering": "moondream:2",
    "video_question_answering": "qwen2-vl:2b-instruct"
  }
}
```

### **Selecting a Profile at Runtime**
- Default: auto-detected. The app uses `regular_sized_models` only if all regular-profile models in `models_mapping.json` are installed. Otherwise, it uses `small_sized_models`.
- Force via env var: `export JOAT_PROFILE=small_sized_models` or `regular_sized_models`
- Programmatic override: `JOATSystem(models_mapping_file="models_mapping.json", profile_key="small_sized_models")`

## 🛠️ **Troubleshooting**

See the [Advanced Guide](docs/ADVANCED_GUIDE.md) for troubleshooting and performance tips.

## 📜 License

The JOAT source code is licensed under the **Apache License 2.0**. You can find the full license text in the [LICENSE](LICENSE) file.

### AI Model Licenses
The AI models used by this project have their own licenses. When you use JOAT, you are also subject to the license terms of the underlying models, which include:
- **Llama 3 Community License**: Applies to models like `llama3` and `codellama`.
- **Apache 2.0**: Applies to models like `mistral`.

It is your responsibility to review and comply with the terms of each model's license and its Acceptable Use Policy.

## 📁 **File Structure**

```
joat/
├── main.py              # CLI version
├── app.py               # Core application logic
├── gui_app.py           # The GUI application window
├── start_gui.sh         # GUI launch script for macOS/Linux
├── ollama_client.py     # Ollama API client
├── setup_ollama.py      # Model setup script (installs regular by default)
├── models_mapping.json  # Task-to-model mapping (profiles)
├── requirements.txt     # Python dependencies
├── docs/                # Documentation files
└── README.md            # This file
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
2. **RAM**: 16GB+ recommended for smooth operation
3. **GPU**: Optional but speeds up inference (if supported by your hardware and Ollama)
4. **Model Selection**: Use smaller models for faster responses

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


---

**Enjoy your local AI assistant! 🤖✨** 
