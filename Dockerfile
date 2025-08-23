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

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set environment variables
ENV DEVICE=cpu
ENV PORT=8080

# Run the FastAPI app with Uvicorn (Cloud Run needs this)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port=8080"]
