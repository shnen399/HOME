#!/usr/bin/env bash
set -euxo pipefail

# Playwright 瀏覽器快取路徑（Render 建議）
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
export PYTHONUNBUFFERED=1
export PORT="${PORT:-10000}"

# 啟動 FastAPI（如檔名不同請改成對應模組:app）
uvicorn main:app --host 0.0.0.0 --port "$PORT"
