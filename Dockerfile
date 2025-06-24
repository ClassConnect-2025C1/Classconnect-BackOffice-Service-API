# --- build stage -----------------------------------------------------------
FROM python:3.11-slim AS builder
WORKDIR /app

# copy the *folder* instead of individual files
COPY requirements.txt .

# build wheels for runtime deps only
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir dist -r requirements.txt

# --- runtime stage ---------------------------------------------------------
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY --from=builder /app/dist /tmp/wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /tmp/wheels/*

COPY src ./src
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
