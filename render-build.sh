#!/usr/bin/env bash
set -euo pipefail

echo "==> 安裝 Python 套件"
pip install --upgrade pip
pip install -r requirements.txt || true

# 確保有安裝 Playwright
if ! python - <<'PY'
import importlib.util, sys
sys.exit(0 if importlib.util.find_spec("playwright") else 1)
PY
then
  pip install playwright
fi

echo "==> 安裝 Chromium 瀏覽器（永久自動安裝）"
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
python -m playwright install chromium --with-deps

echo "==> 構建完成"
