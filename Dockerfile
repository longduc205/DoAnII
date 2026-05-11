FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for lxml
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5000

# Remove any stale SQLite DB so schema is always recreated fresh on startup
RUN rm -f /app/instance/scanner.db /app/scanner.db

# Run the application
CMD ["python", "run.py"]
