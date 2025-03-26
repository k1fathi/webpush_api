FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use shell form to allow environment variable substitution
CMD uvicorn main:app --host $(echo $API_HOST) --port $(echo $API_PORT)
