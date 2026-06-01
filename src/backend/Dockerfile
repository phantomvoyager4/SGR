FROM python:3.12-slim

WORKDIR /app

COPY src/backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend /app/src/
COPY data/search_index.json /app/data/
COPY data/parquet/ /app/data/parquet/

EXPOSE 8000

ENV PYTHONPATH=/app/src/backend
WORKDIR /app/src/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
