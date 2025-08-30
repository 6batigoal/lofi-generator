# Base image: CUDA 12.1 runtime on Ubuntu 22.04
FROM nvidia/cuda:12.1.105-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python 3.11 and system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git ffmpeg wget build-essential \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && python3 -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn google-cloud-storage

# Copy the rest of the application
COPY . .

# Expose Cloud Run default port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV DEVICE=cuda

# Start FastAPI with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]
