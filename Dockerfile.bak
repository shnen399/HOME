FROM python:3.11-slim

# Basic fonts for CJK
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \    && playwright install --with-deps chromium

COPY app ./app

# Writable dir for records/accounts
RUN mkdir -p /data
ENV DATA_DIR=/data

EXPOSE 10000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
