    #!/usr/bin/env bash
    set -e
    echo "[build] Installing Python dependencies..."
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
    # Ensure Playwright Python package is present (in case requirements.txt missed it)
    python - <<'PY'
import importlib, sys, subprocess
try:
    importlib.import_module("playwright")
    print("[build] Playwright package already installed.")
except Exception:
    print("[build] Installing Playwright package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
PY
    echo "[build] Installing Playwright browsers (with OS deps)..."
    playwright install --with-deps
    echo "[build] Done."
