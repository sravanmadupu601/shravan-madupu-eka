FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup appuser

COPY services/embedding-service/requirements.txt .
COPY libraries/eka-ai /opt/eka-ai
RUN pip install --no-cache-dir --upgrade pip \
    && grep -v '^-e ' requirements.txt > /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir /opt/eka-ai

COPY services/embedding-service/app ./app
COPY services/embedding-service/alembic ./alembic
COPY services/embedding-service/alembic.ini services/embedding-service/pyproject.toml ./

USER appuser
EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8002/health/live', timeout=3)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
