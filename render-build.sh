#!/usr/bin/env bash
set -euxo pipefail

# 升級 pip 並安裝 Python 依賴
pip install --upgrade pip
pip install -r requirements.txt

# 安裝 Playwright 的 Chromium 與系統相依套件
python -m playwright install --with-deps chromium

# 若有 Node 前端，安裝依賴（可選）
if [ -f package.json ]; then
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install --force
  fi
fi
