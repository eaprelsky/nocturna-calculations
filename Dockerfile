# Nocturna Calculations - Optimized Multi-Layer Production Docker Image
# Multi-stage build with aggressive caching for fast rebuilds

# ==============================================================================
# Stage 1: Base OS layer (rarely changes - maximum cache reuse)
# ==============================================================================
FROM python:3.11-slim AS base-os

# Set labels for image identification
LABEL maintainer="nocturna-team"
LABEL version="2.0"
LABEL description="Nocturna Calculations Service - Base OS Layer"

# Install system dependencies (this layer is cached unless system packages change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r nocturna && useradd -r -g nocturna nocturna

# ==============================================================================
# Stage 2: Python dependencies layer (changes only when requirements.txt changes)
# ==============================================================================
FROM base-os AS python-deps

WORKDIR /app

# Copy only requirements file first (Docker cache optimization)
COPY requirements.txt .

# Install Python dependencies with caching
# This layer rebuilds only when requirements.txt changes
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# Stage 3: Application layer (changes frequently with code updates)
# ==============================================================================
FROM base-os AS application

WORKDIR /app

# Copy Python packages from dependencies layer
COPY --from=python-deps /root/.local /home/nocturna/.local

# Copy application code (this layer rebuilds on every code change)
COPY --chown=nocturna:nocturna . .

# Make scripts executable
RUN chmod +x scripts/*.py scripts/*.sh 2>/dev/null || true

# Set environment variables
ENV PATH=/home/nocturna/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER nocturna

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# ==============================================================================
# Stage 4: Production target (default)
# ==============================================================================
FROM application AS production

# Production-specific settings
ENV LOG_LEVEL=INFO
ENV DEBUG=false

# Run with production settings
CMD ["uvicorn", "nocturna_calculations.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ==============================================================================
# Stage 5: Staging target
# ==============================================================================
FROM application AS staging

# Staging-specific settings
ENV LOG_LEVEL=DEBUG
ENV DEBUG=true

# Run with fewer workers for staging
CMD ["uvicorn", "nocturna_calculations.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"] 