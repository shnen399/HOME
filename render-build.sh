#!/usr/bin/env bash
set -euxo pipefail

# 1) 升級 pip
pip install --upgrade pip

# 2) 安裝 Python 依賴
pip install -r requirements.txt

# 3) 指定 Playwright 瀏覽器快取路徑（與執行時一致）
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

# 4) 安裝「Python 版」Playwright 的 Chromium（不要用 npx）
python -m playwright install chromium
