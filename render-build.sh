#!/usr/bin/env bash
set -euxo pipefail

# 升級 pip 並安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 設定快取路徑（跟環境變數一致）
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

# 安裝 Playwright 與 Chromium 及依賴
npm install -g playwright
npx --yes playwright install chromium --with-deps

# 開放快取讀取權限
chmod -R a+rX /opt/render/.cache || true
