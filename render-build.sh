#!/usr/bin/env bash

# 升級 pip
pip install --upgrade pip

# 安裝 Python 套件
pip install -r requirements.txt

# 安裝 Playwright Chromium 到指定快取路徑
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
python -m playwright install chromium
