# Start from NVIDIA CUDA runtime
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies and Python 3.11
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    git \
    ffmpeg \
    build-essential \
    ca-certificates \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y python3.11 python3.11-venv python3.11-distutils python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for Python 3.11
RUN python3.11 -m pip install --upgrade pip

# Install PyTorch + CUDA for Python 3.11
RUN python3.11 -m pip install --no-cache-dir \
    torch==2.1.0+cu121 torchvision torchaudio \
    --extra-index-url https://download.pytorch.org/whl/cu121

# Copy requirements and install all Python dependencies safely
COPY requirements.txt .

RUN python3.11 -m pip install --no-cache-dir --break-system-packages -r requirements.txt \
    && python3.11 -m pip install --no-cache-dir uvicorn google-cloud-storage

# Copy application code
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Set environment variables for FastAPI
ENV PORT=8080
ENV DEVICE=cuda

# Start FastAPI with Uvicorn using Python 3.11
CMD ["python3.11", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]

