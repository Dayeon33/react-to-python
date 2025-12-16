FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# cd 폴더 안의 requirements만 설치
COPY cd/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# cd 폴더 안의 앱 코드만 복사
COPY cd/ /app/

EXPOSE 8080

# Cloud Run은 PORT를 자동으로 줌 -> 고정하지 말고 $PORT 사용
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

