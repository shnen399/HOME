FROM python:3.11-slim

# 1) 系統相依 + 之後給 Playwright 用的套件
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates xdg-utils \
    fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
 && rm -rf /var/lib/apt/lists/*

# 2) 安裝 Node.js 18（Playwright 需要 >=18）
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get install -y nodejs

# 3) Python 基本設定
RUN pip install --upgrade pip
WORKDIR /app

# 4) 安裝你的 Python 依賴（請確保 requirements.txt 內含 greenlet 修正）
#   至少要有：
#   greenlet>=3.1,<3.3
#   fastapi
#   uvicorn
#   playwright
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5) 保險：確保關鍵套件存在，並一次把瀏覽器與依賴裝好
RUN pip install fastapi uvicorn playwright \
 && python -m playwright install --with-deps

# 6) 複製程式碼並啟動
COPY . .
ENV PORT=10000
# 如果你的入口不是 main.py 裡的 app，請改成實際模組（例：app.main:app）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
