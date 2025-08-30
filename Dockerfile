# Use NVIDIA PyTorch image with CUDA support (GPU runtime)
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python + system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir uvicorn google-cloud-storage

# Copy the rest of the application
COPY . .

# Expose Cloud Run default port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV DEVICE=cuda

# Fail fast if GPU is missing
RUN python3 -c "import torch; assert torch.cuda.is_available(), '❌ GPU not detected in container'"

# Start FastAPI with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]
