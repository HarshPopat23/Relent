# ==============================================================================
# Multi-stage Dockerfile for Relent AI
# ==============================================================================

# --- Stage 1: Build React Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Backend Runtime ---
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies & ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Create necessary directories
RUN mkdir -p downloads clips reels vector_db whisper_models

EXPOSE 8000 8501 5173

CMD ["python", "server.py"]
