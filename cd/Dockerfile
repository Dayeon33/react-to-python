FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY cd/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY cd/ /app/

ENV PORT=8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
