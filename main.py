from fastapi import FastAPI
from fastapi.responses import JSONResponse
from panel_article import post_article_job
from scheduler import start_scheduler

app = FastAPI()

@app.get("/")
def root():
    return JSONResponse(content={"message": "PIXNET 自動發文系統已啟動"})

@app.post("/post_article")
def post_article():
    return post_article_job()

start_scheduler()
