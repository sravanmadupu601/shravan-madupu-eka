FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY services/mcp-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/mcp-service/app ./app
EXPOSE 8005
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8005"]
