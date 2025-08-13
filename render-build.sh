#!/usr/bin/env bash
set -euxo pipefail

# 安裝編譯工具與系統依賴
apt-get update && apt-get install -y \
    python3-dev build-essential g++ \
    libffi-dev libssl-dev \
    wget curl gnupg ca-certificates \
    fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
 && rm -rf /var/lib/apt/lists/*

# 升級 pip 並安裝 Python 依賴
pip install --upgrade pip
pip install -r requirements.txt

# 安裝 Playwright 的 Chromium（不加 --with-deps 避免需要 root）
python -m playwright install chromium

# 若有 Node 前端，安裝依賴（可選）
if [ -f package.json ]; then
    if [ -f package-lock.json ]; then
        npm ci
    else
        npm install --force
    fi
fi
