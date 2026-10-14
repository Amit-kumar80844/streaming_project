# Python 3.11 on slim Debian — compatible with all dependencies
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pin all dependencies to a coherent set
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Pre-train models at build time so startup is instant
# (Skipped if artifacts already present)
RUN python -c "from pathlib import Path; import models.train_models as tm; tm.run_training_pipeline() if not Path('models/saved/stage2_model.joblib').exists() else print('[Docker build] Models already present.')"

EXPOSE 8000

# Health check so Docker Compose / orchestrators know when the app is ready
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Non-root user for security
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "run.py"]
