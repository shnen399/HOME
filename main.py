from fastapi import FastAPI
from fastapi.responses import JSONResponse
from scheduler import start_scheduler
from panel_article import post_article_once

app = FastAPI(title="PIXNET AutoPoster")

start_scheduler()

@app.get("/")
def root():
    return {"message": "服務正常運行中", "hint": "到 /docs 測試 POST /post_article"}

@app.post("/post_article")
def post_article():
    try:
        result = post_article_once()
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})
