    #!/usr/bin/env bash
    set -e
    # Optional: verify browsers exist (no-op if already installed)
    python - <<'PY'
print("[start] Verifying Playwright import...")
import playwright  # noqa
print("[start] OK.")
PY
    # Start FastAPI app (adjust module:app if different)
    APP_MODULE=${APP_MODULE:-main:app}
    HOST=0.0.0.0
    PORT=${PORT:-10000}
    echo "[start] Launching Uvicorn ${APP_MODULE} on :${PORT}"
    exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"
