FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DB_PATH=/app/data/database.db \
    WEB_SERVER_HOST=0.0.0.0 \
    WEB_SERVER_PORT=8001

WORKDIR /app

COPY req.txt .
RUN pip install -r req.txt

COPY . .
RUN useradd --create-home --uid 1000 bot \
    && mkdir -p /app/data \
    && chown -R bot:bot /app
USER bot

VOLUME ["/app/data"]
EXPOSE 8001

CMD ["python", "main.py"]
