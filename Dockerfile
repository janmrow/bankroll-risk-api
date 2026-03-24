FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# SECURITY FIX: Create a dedicated non-root user
RUN useradd -m appuser

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --no-dev --frozen

COPY app ./app

# SECURITY FIX: Switch to the unprivileged user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
