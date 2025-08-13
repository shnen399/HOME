#!/usr/bin/env bash
set -euxo pipefail

export PORT="${PORT:-10000}"
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
export PIP_DISABLE_PIP_VERSION_CHECK=1

# 啟動前自我修復：若沒安裝瀏覽器就補裝一次
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
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
PY

# 啟動 FastAPI（若 app 位置不同請調整 main:app）
exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips='*'
