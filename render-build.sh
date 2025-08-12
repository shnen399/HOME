#!/usr/bin/env bash
set -euxo pipefail

# 安裝 Python 套件
pip install -r requirements.txt

# 安裝 Playwright Chromium 瀏覽器與系統依賴
playwright install chromium
playwright install-deps || true
