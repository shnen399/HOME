import os, sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from core import ensure_db, get_logs, generate_article, add_log_row
from poster import post_all

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS","180"))
ACCOUNTS_FILE = "pixnet_accounts.txt"

app = FastAPI(title="PIXNET Ready-To-Run")
app.mount("/static", StaticFiles(directory="static"), name="static")
sch = BackgroundScheduler(timezone="Asia/Taipei")

def job():
    title, content, tags = generate_article()
    res = post_all(ACCOUNTS_FILE, title, content, tags=tags, headless=True)
    for r in res:
        add_log_row(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), r.get("email"), title, "success" if r["ok"] else "fail", r.get("msg"))

@app.on_event("startup")
def start():
    ensure_db()
    sch.add_job(job, "interval", seconds=INTERVAL_SECONDS, id="auto", replace_existing=True)
    sch.start()

@app.get("/")
def root():
    return {"status":"running","interval_seconds":INTERVAL_SECONDS}

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return HTMLResponse(open("static/ui.html","r",encoding="utf-8").read())

@app.get("/accounts", response_class=PlainTextResponse)
def accounts():
    try: return PlainTextResponse(open("pixnet_accounts.txt","r",encoding="utf-8").read())
    except: return PlainTextResponse("")

@app.get("/logs")
def logs(limit: int=100):
    return get_logs(limit)

@app.post("/post_article")
def post_article():
    try:
        title, content, tags = generate_article()
        res = post_all(ACCOUNTS_FILE, title, content, tags=tags, headless=True)
        return JSONResponse({"ok": True, "result": res})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})
