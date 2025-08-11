from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
from core import post_article_once

app = FastAPI(title="PIXNET AutoPoster")

@app.get("/")
def root():
    return {"message": "PIXNET 自動發文系統已啟動"}

@app.post("/post_article")
def post_article():
    try:
        res = post_article_once()
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

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
