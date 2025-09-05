# Start from NVIDIA CUDA runtime
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies, Python 3.11, and HTTPS transport for apt
RUN apt-get update && apt-get install -y --fix-missing --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    wget \
    git \
    ffmpeg \
    build-essential \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --fix-missing \
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip inside venv
RUN pip install --upgrade pip

# Install PyTorch + CUDA
RUN pip install --no-cache-dir torch==2.1.0+cu121 torchvision torchaudio \
    --extra-index-url https://download.pytorch.org/whl/cu121

# Copy requirements.txt and install all Python dependencies inside venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn google-cloud-storage

# Copy application code
COPY . .

# Expose Cloud Run port
EXPOSE 8080

# Set environment variables for FastAPI
ENV PORT=8080
ENV DEVICE=cuda

# Start FastAPI with Uvicorn inside the venv
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]