# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose only Cloud Run port
EXPOSE 8080

# Cloud Run provides PORT env variable automatically
ENV DEVICE=cpu
ENV PORT=8080

# Start FastAPI
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
