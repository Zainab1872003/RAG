FROM python:3.10.0-slim AS builder

WORKDIR /build

# Install build dependencies
# Using --no-install-recommends reduces image size
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install your requirements
COPY requirements.txt .
# It's a good practice to install heavy or specific packages first
RUN pip install --no-cache-dir 'numpy<2'
RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# --- Runtime stage - smaller final image ---
FROM python:3.10.0-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy ONLY the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your application code
# Assuming your main FastAPI app is in the 'app' directory
COPY app/ ./app/

# Create non-root user for security
# Also create necessary directories and set permissions
RUN mkdir -p /app/uploaded_docs /app/logs && \
    useradd -m -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check to ensure the API is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Correct CMD to run uvicorn and bind to 0.0.0.0
# This makes the backend_run.py script unnecessary for the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
