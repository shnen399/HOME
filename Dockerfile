FROM python:3.11-slim

# 1) 系統相依（Playwright/Chromium 會用到）
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates xdg-utils \
    fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
 && rm -rf /var/lib/apt/lists/*

# 2)（必要）安裝 Node.js，Playwright CLI 需要
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get install -y nodejs \
 && node -v && npm -v

# 3) Python 套件
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 4) 建置階段就把 Chromium 裝好（含系統依賴）
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright && \
    python -m playwright install --with-deps chromium && \
    ls -R /ms-playwright

# 5) 複製程式碼
COPY . .

# 6) 啟動（如果不是 main.py / app，請改成你的檔名與變數名）
ENV PORT=10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
