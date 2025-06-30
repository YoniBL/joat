# 🏠 JOAT Local Setup Guide

This guide will help you set up JOAT to run locally using Ollama models, eliminating the need for expensive cloud APIs.

## 🎯 **Benefits of Local Setup**

- ✅ **No API costs** - All processing happens locally
- ✅ **Privacy** - Your data never leaves your computer
- ✅ **Offline operation** - Works without internet after setup
- ✅ **Full control** - Customize models and parameters
- ✅ **No rate limits** - Use as much as you want

## 📋 **System Requirements**

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB free space for models
- **OS**: macOS, Linux, or Windows
- **Python**: 3.7 or higher

## 🚀 **Quick Setup**

### **Step 1: Install Ollama**

#### **macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### **Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

### **Step 2: Start Ollama**
```bash
ollama serve
```

### **Step 3: Setup JOAT**
```bash
# Clone or navigate to your JOAT directory
cd joat

# Install Python dependencies
pip install -r requirements.txt

# Run the automated setup
python setup_ollama.py
```

### **Step 4: Test the System**
```bash
python app.py
# or
python app_launcher.py
```

## 📦 **Available Models**

JOAT uses these local models:

| Model | Purpose | Size | Description |
|-------|---------|------|-------------|
| `codellama` | Coding | ~4GB | Code generation and programming |
| `llama3` | General | ~4GB | Text generation and reasoning |
| `wizard-math` | Math | ~4GB | Mathematical problem solving |
| `llava` | Vision | ~4GB | Image analysis and visual Q&A |

## 🔧 **Manual Setup (Alternative)**

If the automated setup doesn't work, here's the manual process:

### **1. Install Models Manually**
```bash
# Install each model
ollama pull codellama
ollama pull llama3
ollama pull wizard-math
ollama pull llava
```

### **2. Verify Installation**
```bash
# List installed models
ollama list
```

### **3. Test a Model**
```bash
# Test code generation
ollama run codellama "Write a Python function to calculate fibonacci numbers"
```

## 🎮 **Usage**

### **Basic Usage**
```bash
python app.py
# or
python app_launcher.py
```

### **Special Commands**
- `status` - Check Ollama and model status
- `history` - View conversation history
- `clear` - Clear conversation history
- `quit` - Exit the application

### **Example Interactions**
```
You: Write a Python function to calculate factorial
🤖 [Response from codellama]

You: Solve the equation 2x + 5 = 13
🤖 [Response from wizard-math]

You: Explain quantum physics
🤖 [Response from llama3]
```

## 🔍 **Troubleshooting**

### **Ollama Not Running**
```bash
# Start Ollama
ollama serve

# Check if it's running
ollama list
```

### **Model Not Found**
```bash
# Pull the missing model
ollama pull modelname

# Check available models
ollama list
```

### **Out of Memory**
- Close other applications
- Use smaller models
- Increase system RAM

### **Slow Performance**
- Use SSD storage
- Increase RAM
- Close unnecessary applications
- Use smaller models for faster responses

## ⚙️ **Configuration**

### **Model Parameters**
You can customize model behavior in `ollama_client.py`:

```python
# Adjust these parameters
max_tokens=1000      # Response length
temperature=0.7      # Creativity (0.0-1.0)
top_p=0.9           # Response diversity
```

### **Custom Models**
Add your own models to `models_mapping.txt`:

```
{your_task: your_model_name}
```

## 📊 **Performance Tips**

### **For Better Speed:**
- Use SSD storage
- Close other applications
- Use smaller models
- Increase system RAM

### **For Better Quality:**
- Use larger models
- Increase max_tokens
- Adjust temperature for creativity

## 🔒 **Security & Privacy**

- ✅ All data stays on your computer
- ✅ No internet required after setup
- ✅ No API keys needed
- ✅ No usage tracking
- ✅ Full control over models

## 🆘 **Getting Help**

### **Common Issues:**

1. **"Ollama not running"**
   - Run `ollama serve` in a separate terminal
   - Check if Ollama is installed: `ollama --version`

2. **"Model not found"**
   - Pull the model: `ollama pull modelname`
   - Check available models: `ollama list`

3. **"Out of memory"**
   - Close other applications
   - Use smaller models
   - Increase system RAM

4. **"Slow responses"**
   - Use SSD storage
   - Close unnecessary applications
   - Use smaller models

### **Getting Support:**
- Check Ollama documentation: [https://ollama.ai/docs](https://ollama.ai/docs)
- GitHub issues for specific problems
- Community forums for general questions

## 🎉 **Success!**

Once setup is complete, you have:
- ✅ Local AI processing
- ✅ No ongoing costs
- ✅ Privacy protection
- ✅ Offline capability
- ✅ Full control

Enjoy your local AI assistant! 🤖 