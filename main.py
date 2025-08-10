from fastapi import FastAPI
from scheduler import start_scheduler
from panel_article import post_article_job

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "PIXNET 自動發文系統已啟動"}

@app.post("/post_article")
def post_article():
    return post_article_job()
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from panel_article import post_article_once  # 匯入你已經寫好的發文函式

app = FastAPI()

@app.get("/")
def root():
return {"message": "服務正常運行中"}

@app.post("/post_article")
def post_article():
try:
result = post_article_once()  # 直接呼叫發文
return JSONResponse({"ok": True, "result": result})
except Exception as e:
return JSONResponse({"ok": False, "error": str(e)})
