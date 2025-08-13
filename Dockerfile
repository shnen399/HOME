FROM python:3.11-slim

# 1) 安裝 Playwright 需要的系統依賴
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates xdg-utils \
    fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
 && rm -rf /var/lib/apt/lists/*

# 2) 安裝 Node.js 18（Playwright 必需）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get install -y nodejs

# 3) 升級 pip
RUN pip install --upgrade pip

# 4) 設定工作目錄
WORKDIR /app

# 5) 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 6) 設定 Playwright 瀏覽器路徑並安裝 Chromium（含系統依賴）
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright && python -m playwright install --with-deps chromium

# 7) 複製專案檔案
COPY . .

# 8) 設定埠號
ENV PORT=10000

# 9) 啟動應用程式（依你的程式檔名調整 main:app）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
