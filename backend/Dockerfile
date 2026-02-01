FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any (e.g. for psycopg2 if binary not enough, or pandas/numpy build deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
# Only copying what's needed for the backend app
COPY . .

# Expose port (Railway defaults to PORT env var, but 8000 is our dev default)
EXPOSE 8000

# Run command
# We use shell form to allow variable expansion if needed, but array form is safer.
# Using HOST 0.0.0.0 is crucial for containers.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
