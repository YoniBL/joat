# Advanced User Guide

This guide provides advanced configuration, troubleshooting, and performance tips for JOAT.

## 🔧 Configuration

### Customizing Model Behavior
You can fine-tune the performance of the AI models by adjusting parameters in `ollama_client.py`:

```python
# In OllamaClient.generate_response
payload = {
    # ...
    "options": {
        "num_predict": 1000,      # Max tokens in the response
        "temperature": 0.7,     # Creativity (0.0=deterministic, 1.0=creative)
        "top_p": 0.9,           # Response diversity
        "repeat_penalty": 1.1   # Reduces word repetition
    }
}
```

### Adding and Using Custom Models
1.  **Install the Model**: Pull your desired model using Ollama.
    ```bash
    ollama pull your-custom-model
    ```
2.  **Map the Model**: Open `models_mapping.txt` and assign your model to a new or existing task.
    ```
    {
      "summarization": "your-custom-model",
      ...
    }
    ```
3.  **Restart and Use**: Restart JOAT, and it will now use your custom model for the specified task.

## 📊 Performance Tips

### For Better Speed
*   **Use an SSD**: Solid-state drives provide much faster model loading times.
*   **Increase RAM**: More RAM allows the system to handle larger models more efficiently. 16GB is recommended.
*   **Use Smaller Models**: If speed is a priority, consider using smaller, distilled models that are optimized for performance.
*   **Close Other Applications**: Freeing up system resources will improve response times.

### For Better Quality
*   **Use Larger Models**: Larger models generally provide more accurate and coherent responses.
*   **Adjust `max_tokens`**: If responses are getting cut off, increase the `num_predict` (max tokens) value.
*   **Tune `temperature`**: For more creative and varied responses, increase the temperature. For more deterministic and factual answers, lower it.

## 🔍 Troubleshooting

### "Ollama not running"
This is the most common issue. To resolve it:
1.  Open a new terminal window.
2.  Run the command: `ollama serve`
3.  To verify it's running, you can use: `ollama list`

### "Model not found"
If the application reports that a model is not found, you can manually pull it:
```bash
# Replace 'model-name' with the actual model you need
ollama pull model-name
```
You can see all locally installed models with `ollama list`.

### "Out of Memory"
Running large language models is memory-intensive. If you encounter this error:
*   Close other memory-heavy applications.
*   Consider using a smaller model from the Ollama library.
*   If possible, upgrade your system's RAM. 