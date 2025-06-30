# AI Models in JOAT

This document provides an overview of the specialized AI models used in the JOAT system.

## Default Model Configuration

JOAT is designed to use a suite of specialized models, each chosen for its strength in a specific domain. This multi-model approach ensures that your queries are handled by the most capable AI for the job.

The default model-to-task mappings are defined in `models_mapping.txt`.

| Task Category | Default Model | Description |
|---|---|---|
| **Code Generation** | `codellama` | A top-tier model for generating, debugging, and explaining code in various programming languages. |
| **Text Generation** | `llama3` | A powerful and versatile model for creative writing, general conversation, and complex text generation. |
| **Math & Reasoning** | `wizard-math` | A model specifically fine-tuned for solving mathematical problems and logical reasoning. |
| **Q&A & Summarization** | `mistral` | An efficient and accurate model for answering factual questions and summarizing text. |
| **Commonsense & Sentiment** | `phi3` | A compact but capable model that excels at commonsense reasoning and analyzing sentiment. |
| **Vision (Optional)**| `llava` | An optional model for analyzing and answering questions about images. |

## Customizing Models

You are not limited to the default models. You can use any model available from the [Ollama Library](https://ollama.ai/library) by following the instructions in the [Advanced User Guide](./ADVANCED_GUIDE.md). 