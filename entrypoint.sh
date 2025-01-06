#!/bin/bash
set -e

# Start Ollama in the background with your preferred model
ollama serve --model llama3.2:1b &

# Small sleep to give Ollama some time to initialize
sleep 15

# Now run your Python code
python src/main.py