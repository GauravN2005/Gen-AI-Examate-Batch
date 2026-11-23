# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl binutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    # Remove C++ headers and tests in PyTorch that are never used at runtime
    && rm -rf /usr/local/lib/python3.11/site-packages/torch/include \
    && rm -rf /usr/local/lib/python3.11/site-packages/torch/test \
    # Remove test directories and pycache across all other installed packages
    && find /usr/local/lib/python3.11/site-packages -type d -name "tests" -not -path "*/torch/*" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete \
    # Strip debugging symbols from shared object libraries to save space
    && find /usr/local/lib/python3.11/site-packages -name "*.so*" -exec strip --strip-unneeded {} + 2>/dev/null || true \
    && apt-get remove -y binutils \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*

COPY app ./app
COPY prompts ./prompts
COPY data/records.json ./data/records.json
COPY data/sample_records.json ./data/sample_records.json

# Pre-index vector database and pre-download embedding model for instant startup
RUN python -m app.vectorstore \
    && find /root/.cache/huggingface -type f -name "*.bin" -delete 2>/dev/null || true \
    && rm -rf /tmp/*

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://127.0.0.1:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
