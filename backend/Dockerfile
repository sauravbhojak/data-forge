# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer caching)
COPY pyproject.toml ./

# Install production dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]" --target /install

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# Security: non-root user
RUN groupadd --gid 1001 dataforge && \
    useradd --uid 1001 --gid dataforge --shell /bin/bash --create-home dataforge

# Copy installed packages from builder
COPY --from=builder /install /usr/local/lib/python3.13/site-packages

# Copy application source
COPY --chown=dataforge:dataforge app/ ./app/

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

USER dataforge

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop"]
