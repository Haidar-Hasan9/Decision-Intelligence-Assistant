FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for sentence-transformers
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy dependency files and install
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]