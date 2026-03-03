# ---------- builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY pyproject.toml .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels .[dev]

# ---------- final ----------
FROM python:3.11-slim

RUN addgroup --system app && adduser --system --ingroup app app

ENV HOME=/home/app
ENV APP_HOME=/home/app/app
WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/* && \
    rm -rf /wheels

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME

USER app

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
