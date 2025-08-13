from fastapi import FastAPI
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = FastAPI(title="PIXNET AutoPoster")

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
log = logging.getLogger(__name__)

# 測試文章生成函數
def article_generator():
    return (
        "自動發文：測試標題",
        """<h2>測試內文</h2><p>這是後備內文，代表你的 article_generator 還沒就緒。</p>""",
        ["自動", "測試"]
    )

def post_article_once():
    title, content, tags = article_generator()
    log.info(f"準備發文：{title}")
    # 這裡放實際發文邏輯，例如調用 PIXNET API
    return {"status": "success", "title": title}

# 排程器設定
scheduler = BackgroundScheduler(timezone="Asia/Taipei")

def _job():
    try:
        res = post_article_once()
        log.info(f"自動發文結果：{res}")
    except Exception as e:
        log.exception(f"自動發文錯誤：{e}")

def start_scheduler():
    try:
        scheduler.add_job(_job, "interval", minutes=3, id="auto_post", replace_existing=True)
        scheduler.start()
        log.info("Scheduler 啟動完成（每 3 分鐘執行一次）。")
    except Exception as e:
        log.exception(f"啟動排程失敗：{e}")

# 啟動排程
start_scheduler()

@app.get("/")
def root():
    return {"message": "PIXNET 自動發文系統已啟動"}

@app.get("/post_article")
def post_article():
    res = post_article_once()
    return JSONResponse(content=res)
