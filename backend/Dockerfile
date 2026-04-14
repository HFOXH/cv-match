FROM python:3.11-slim

# Don't buffer stdout/stderr — so `docker logs` sees output immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python dependencies first so the layer caches when only source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source.
COPY . .

# uvicorn must bind to 0.0.0.0 to be reachable from the host / other containers.
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
