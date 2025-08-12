# Render Playwright Fix (drop-in scripts)

This package provides two scripts to fix the "BrowserType.launch: Executable doesn't exist" error on Render
by installing Playwright browsers during the build step.

## Files
- `render-build.sh` — Build script. Installs requirements and runs `playwright install --with-deps`.
- `startup.sh` — Start script. Boots your FastAPI app via Uvicorn.

## How to use on Render
1. Upload both scripts to your project root (same level as `requirements.txt` and `main.py`).
2. Set permissions (if needed): `chmod +x render-build.sh startup.sh`.
3. In Render:
   - **Build Command:** `bash render-build.sh`
   - **Start Command:** `bash startup.sh`
4. Make sure your `requirements.txt` includes `playwright` and `uvicorn`.
   - If not, add:
     ```
     playwright
     uvicorn
     ```
5. Redeploy.

## Note
If your app entrypoint is not `main:app`, set env var `APP_MODULE` to the correct module path,
e.g. `app.main:app`.
