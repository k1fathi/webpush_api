FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make scripts executable
RUN mkdir -p /app/scripts
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies with verbose output
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -v -r requirements.txt

# Copy the project
COPY . .

# Create backup directory
RUN mkdir -p /app/db_backups

# Set environment variables
ENV PYTHONPATH=/app/webpush_api
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
