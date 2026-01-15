
# Base Image: Lightweight Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and general utilities
# libgl1 and libglib2.0-0 are required for cv2 even in headless mode
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY core/ core/
COPY static/ static/
COPY models/ models/

# Expose port (FastAPI default)
EXPOSE 8000

# Command to allow running with $PORT injection (common in PaaS like Render/Railway)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
