# Nocturna Calculations - Production Docker Image
# Multi-stage build for optimal size and security

# Build stage
FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Create non-root user for security
RUN groupadd -r nocturna && useradd -r -g nocturna nocturna

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/nocturna/.local

# Copy application code
COPY . .

# Change ownership to nocturna user
RUN chown -R nocturna:nocturna /app

# Switch to non-root user
USER nocturna

# Make sure scripts are executable
USER root
RUN chmod +x scripts/*.py scripts/*.sh 2>/dev/null || true
USER nocturna

# Set environment variables
ENV PATH=/home/nocturna/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "nocturna_calculations.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"] 