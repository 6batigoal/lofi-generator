# Use PyTorch image with Python 3.11 and CUDA 12.1
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime-py3.11

# Set working directory
WORKDIR /app

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn google-cloud-storage

# Copy application code
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV DEVICE=cuda

# Start FastAPI with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]
