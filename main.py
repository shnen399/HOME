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
