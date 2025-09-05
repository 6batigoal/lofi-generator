# Use NVIDIA PyTorch image with Python 3.11 and CUDA 12.1 preinstalled
FROM nvcr.io/nvidia/pytorch:23.08-py3

# Set working directory
WORKDIR /app

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    wget \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn google-cloud-storage

# Copy application code
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Environment variables
ENV PORT=8080
ENV DEVICE=cuda

# Start FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]