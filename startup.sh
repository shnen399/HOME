#!/usr/bin/env bash
set -euxo pipefail

export PORT="${PORT:-10000}"
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

python - <<'PY'
import os, pathlib, subprocess, sys
base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/render/.cache/ms-playwright")
p = pathlib.Path(base)
if not any(p.rglob("headless_shell")):
    print("[startup] chromium not found, installing...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
PY

exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
