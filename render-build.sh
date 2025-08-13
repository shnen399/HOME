#!/usr/bin/env bash
set -euxo pipefail

pip install --upgrade pip
pip install -r requirements.txt

export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
python -m playwright install chromium
