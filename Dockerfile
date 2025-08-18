FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for data files
RUN mkdir -p data

# Copy application code
COPY . .

# Make sure the preprocessing script is executable
RUN chmod +x preprocess_kb.py

# Command to run the preprocessing pipeline
RUN python preprocess_kb.py

# Expose port for LiveKit agent
EXPOSE 8080

# Command to run the application
CMD ["python", "caller_agent.py"]