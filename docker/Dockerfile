# Multi-stage build for pymono
# Stage 1: Build stage with dependencies
FROM python:3.13-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Stage 2: Runtime stage
FROM python:3.13-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser treasury ./treasury
COPY --chown=appuser:appuser pyproject.toml ./
RUN rm -f ./treasury/.env.*
RUN ls -la ./treasury

# Copy sample SQLite database to temp folder for the app to find
COPY --chown=appuser:appuser docker/sample_sql_lite_db/treasury_db_local.db /tmp/treasury_db_local.db

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create directory for logs
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Health check endpoint (adjust port as needed)
HEALTHCHECK --interval=5s --timeout=4s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Default command (can be overridden)
ENTRYPOINT ["python"]
CMD ["treasury/services/gateways/ttb_api/__main__.py"]