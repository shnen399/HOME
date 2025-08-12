#!/usr/bin/env bash
set -euxo pipefail

# 若 build 階段沒裝好，這裡補裝一次
if ! [ -f "/opt/render/.cache/ms-playwright" ] || ! ls /opt/render/.cache/ms-playwright/*/chrome-linux/headless_shell >/dev/null 2>&1; then
  playwright install chromium
  playwright install-deps || true
fi

# 啟動 FastAPI（Render 會提供 $PORT）
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
