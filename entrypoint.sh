#!/bin/bash
set -e

# Start Ollama
ollama serve &

# Wait for Ollama to start
sleep 15

# Pull the model at runtime
ollama pull llama3.1:8b

# Now run your Python code
python src/main.py