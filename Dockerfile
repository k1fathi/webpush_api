FROM python:3.9

WORKDIR /app

# Install required packages with correct package names
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the wait-for-it script executable
RUN chmod +x /app/scripts/wait-for-it.sh

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# The actual command will be provided by docker-compose

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1
