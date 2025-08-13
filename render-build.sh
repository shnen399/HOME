#!/usr/bin/env bash
set -euo pipefail

echo "==> 設定 Playwright 瀏覽器快取路徑"
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

echo "==> 安裝 Playwright Chromium 瀏覽器（含系統依賴）"
npx --yes playwright@1.46.0 install chromium --with-deps

echo "==> Playwright 瀏覽器安裝完成"
