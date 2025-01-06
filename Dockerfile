# Use a lightweight Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies needed for Ollama
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    # optional: for building or debugging
    # build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -L https://cdn.ollama.ai/apt/gpg | gpg --dearmor | tee /usr/share/keyrings/ollama.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/ollama.gpg] https://cdn.ollama.ai/apt . main" > /etc/apt/sources.list.d/ollama.list
RUN apt-get update && apt-get install -y ollama

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Pull the latest Ollama version
RUN ollama pull llama3.2:1b

# Expose the default Ollama port if you need external access
EXPOSE 11411

# Copy an entrypoint script that will run Ollama in the background,
# then start your Python application
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Avoid Python writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Final command that starts everything
CMD ["/entrypoint.sh"]
