FROM python:3.12-slim

WORKDIR /app

COPY services/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/backend/app ./app
COPY src ./src
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
