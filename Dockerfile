FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create scripts directory and set permissions with proper ownership
RUN mkdir -p /app/scripts && \
    chown -R root:root /app/scripts && \
    chmod -R 755 /app/scripts

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script first and set explicit permissions
COPY scripts/docker-entrypoint.sh /app/scripts/
RUN chmod 755 /app/scripts/docker-entrypoint.sh && \
    chown root:root /app/scripts/docker-entrypoint.sh && \
    # Convert Windows line endings to Unix
    sed -i 's/\r$//' /app/scripts/docker-entrypoint.sh

# Copy the rest of the project
COPY . .

# Create backup directory with proper permissions
RUN mkdir -p /app/db_backups && \
    chmod -R 777 /app/db_backups

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
