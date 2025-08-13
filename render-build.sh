#!/usr/bin/env bash
# 升級 pip
pip install --upgrade pip

# 安裝 Python 套件
pip install -r requirements.txt

# 安裝 Playwright Chromium 瀏覽器
npx playwright install chromium
