#!/usr/bin/env bash
set -euo pipefail

echo "==> 安裝 Playwright 需要的系統依賴"
apt-get update
apt-get install -y wget curl gnupg ca-certificates \
  fonts-liberation libasound2 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
  libnss3 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
  libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxshmfence1 \
  && rm -rf /var/lib/apt/lists/*

echo "==> 設定 Playwright 快取目錄（加速下次部署）"
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

echo "==> 安裝 Playwright 的 Chromium（含系統依賴）"
npx --yes playwright@1.46.0 install chromium --with-deps

echo "==> 完成瀏覽器安裝"
