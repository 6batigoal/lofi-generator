# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pyngrok streamlit uvicorn

# Copy the rest of the application code
COPY . .

# Expose ports
EXPOSE 8080 8501

# Set environment variables
ENV DEVICE=cpu
ENV PORT=8080
ENV STREAMLIT_PORT=8501

# Default command for Cloud Run: FastAPI only
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]

