#!/usr/bin/env bash
set -euxo pipefail

# ===== 基本環境 =====
# Render 會提供 $PORT；若本機手動跑，預設用 10000
export PORT="${PORT:-10000}"
# 讓 Playwright 的瀏覽器放在跟執行時一致的位置
export PLAYWRIGHT_BROWSERS_PATH="/opt/render/.cache/ms-playwright"
# 避免 pip 自動檢查更新拖慢啟動
export PIP_DISABLE_PIP_VERSION_CHECK=1

# ===== Playwright 啟動自我修復 =====
# 若快取路徑裡沒有 headless_shell，就在啟動時自動安裝一次 Chromium
python - <<'PY'
import os, pathlib, subprocess, sys
base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/render/.cache/ms-playwright")
need = True
p = pathlib.Path(base)
if p.exists():
    for x in p.rglob("headless_shell"):
        if x.is_file():
            print(f"[startup] chromium found at: {x}")
            need = False
            break
if need:
    print("[startup] chromium not found, installing via Python Playwright ...", flush=True)
    # 用 Python 版 Playwright 安裝（不是 npx）
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
PY

# ===== 啟動你的 FastAPI =====
# 如果你的應用模組不是 main:app，請把下面的 "main:app" 換成正確路徑
exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips='*'
