FROM python:3.11-slim

# 安裝系統必要套件
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
WORKDIR /app

# 安裝 Python 套件
COPY requirements.txt .
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

RUN pip install fastapi uvicorn playwright

# 安裝 Playwright 瀏覽器依賴
RUN python -m playwright install --with-deps

COPY . .

ENV PORT=10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
