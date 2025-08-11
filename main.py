from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from scheduler import start_scheduler
from core import post_article_once  # ✅ 改用 core 的流程

app = FastAPI(title="PIXNET AutoPoster")

# 啟動排程（若已在跑，start_scheduler 會自動略過）
start_scheduler()

@app.get("/")
def root():
    return {"message": "服務已啟動，請到 /docs 測試 POST /post_article"}

@app.post("/post_article")
def post_article():
    try:
        result = post_article_once()  # 會同時寫三種紀錄 & 打 Log
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})

# ===== 下面三個端點：直接查看紀錄檔 =====
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
