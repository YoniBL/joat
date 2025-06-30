#!/bin/bash

# JOAT GUI Launcher Script
# This script launches the JOAT desktop GUI application

echo "🚀 Starting JOAT Desktop GUI..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "gui_app.py" ]; then
    echo "❌ Error: gui_app.py not found in current directory"
    echo "Please run this script from the joat directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if tkinter is available
if ! python -c "import tkinter" &> /dev/null; then
    echo "❌ Error: Tkinter is not available"
    echo "Please install Python with Tkinter support"
    exit 1
fi

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Warning: Ollama is not running"
    echo "   The app will work but may not be able to process requests"
    echo "   To start Ollama: brew services start ollama"
fi

echo ""
echo "🎯 Launching JOAT GUI..."
echo "   Press Ctrl+C to exit"
echo ""

# Launch the GUI app
python3 gui_app.py 