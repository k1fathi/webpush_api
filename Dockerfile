# --- Build Stage ---
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create requirements.txt with necessary packages
RUN echo "fastapi>=0.68.0,<0.69.0\n\
    uvicorn>=0.15.0,<0.16.0\n\
    sqlalchemy>=1.4.0\n\
    psycopg2-binary>=2.9.0\n\
    asyncpg>=0.25.0\n\
    celery>=5.2.0\n\
    redis>=4.0.0\n\
    pydantic>=1.8.0\n\
    alembic>=1.7.0\n\
    python-jose>=3.3.0\n\
    passlib>=1.7.4\n\
    python-multipart>=0.0.5\n\
    aiohttp>=3.8.0\n\
    " > requirements.txt

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Final Stage ---
FROM python:3.10-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Install runtime dependencies (like postgresql-client if needed by entrypoint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder stage
COPY --from=builder /app /app

# Copy the rest of the project
COPY . .

# Copy security scripts and ensure they are executable
COPY ./scripts/docker-entrypoint.sh /app/scripts/docker-entrypoint.sh
COPY ./scripts/wait-for-it.sh /app/scripts/wait-for-it.sh
RUN chmod +x /app/scripts/docker-entrypoint.sh && \
    chmod +x /app/scripts/wait-for-it.sh

# Create directories and set permissions for the non-root user
RUN mkdir -p /app/db_backups /app/static/js && \
    chown -R app:app /app/db_backups /app/static && \
    chmod -R 755 /app/static

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Default command
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
