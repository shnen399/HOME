from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from scheduler import start_scheduler
from core import post_article_once  # ✅ 用 core 版本，才有三種紀錄

app = FastAPI(
    title="PIXNET AutoPoster",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

start_scheduler()

@app.get("/")
def root():
    return {"message": "服務已啟動，請到 /docs 測試 POST /post_article"}

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/post_article")
def post_article():
    try:
        result = post_article_once()  # 會寫三種紀錄
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})

# 三個紀錄檔查看
@app.get("/records/post", response_class=PlainTextResponse)
def get_post_records():
    try:
        return open("發文紀錄.txt", "r", encoding="utf-8").read()
    except FileNotFoundError:
        return "尚無發文紀錄"

@app.get("/records/news", response_class=PlainTextResponse)
def get_news_records():
    try:
        return open("新聞紀錄.txt", "r", encoding="utf-8").read()
    except FileNotFoundError:
        return "尚無新聞紀錄"

@app.get("/records/keywords", response_class=PlainTextResponse)
def get_kw_records():
    try:
        return open("關鍵字紀錄.txt", "r", encoding="utf-8").read()
    except FileNotFoundError:
        return "尚無關鍵字紀錄"
