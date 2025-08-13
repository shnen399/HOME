
#!/usr/bin/env bash
set -euo pipefail

# 讓 Playwright 使用可寫入的快取目錄（Render 可寫）
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
mkdir -p "$PLAYWRIGHT_BROWSERS_PATH"

# 第一次啟動才下載 Chromium，之後會用快取
if ! ls "$PLAYWRIGHT_BROWSERS_PATH" 2>/dev/null | grep -q chromium; then
  echo "==> 安裝 Playwright Chromium（啟動時安裝，避免 build 失敗）"
  npx --yes playwright@1.46.0 install chromium || true
fi

echo "==> 啟動應用程式"
# 依你的專案調整；下方順序會依次嘗試
(uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}) \
  || (python main.py) \
  || (gunicorn app:app --bind 0.0.0.0:${PORT:-10000}) \
  || (node server.js)
