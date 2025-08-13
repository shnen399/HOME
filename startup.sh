#!/usr/bin/env bash
set -euxo pipefail

# 與 build 階段一致：讓 Playwright 用固定快取位置
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

# Render 會注入 $PORT；若本地測試則預設 10000
PORT="${PORT:-10000}"

# 啟動 FastAPI（main.py 裡的 app）
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --proxy-headers \
  --forwarded-allow-ips="*"
