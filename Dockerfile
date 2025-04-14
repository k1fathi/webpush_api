FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    dos2unix \
    netcat-traditional \
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

# Copy all script files first and set permissions
COPY scripts/ /app/scripts/
RUN find /app/scripts/ -type f -name "*.sh" -exec dos2unix {} \; && \
    find /app/scripts/ -type f -name "*.sh" -exec chmod +x {} \; && \
    chown -R root:root /app/scripts/

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
