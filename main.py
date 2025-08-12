from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

# 這兩個 import 可能會間接載入很多東西，建議保留在頂部，
# 但 scheduler 啟動一定要 try/except，避免整個 app 起不來。
try:
    from scheduler import start_scheduler
except Exception as e:
    start_scheduler = None
    print(f"[WARN] import scheduler 失敗：{e}")

try:
    from core import post_article_once
except Exception as e:
    # 讓 /docs 與 /healthz 仍可用
    post_article_once = None
    print(f"[WARN] import core.post_article_once 失敗：{e}")

app = FastAPI(
    title="PIXNET AutoPoster",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 啟動排程（不讓它把整個 API 帶崩）
try:
    if start_scheduler:
        start_scheduler()
    else:
        print("[WARN] 排程未啟動（scheduler 未載入）")
except Exception as e:
    print(f"[WARN] start_scheduler 失敗：{e}")

@app.get("/", response_class=JSONResponse)
def root():
    return {"message": "服務正常運行中", "hint": "到 /docs 測試 POST /post_article"}

@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "OK"

@app.post("/post_article", response_class=JSONResponse)
def post_article():
    if not post_article_once:
        return JSONResponse(
            {"ok": False, "error": "post_article_once 未載入，請查看啟動日誌"},
            status_code=500,
        )
    try:
        result = post_article_once()
        return {"ok": True, "result": result}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
