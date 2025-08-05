import os
import logging
from fastapi import FastAPI
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

try:
    from article_generator import generate_article
    from utils import post_to_pixnet
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from article_generator import generate_article
    from utils import post_to_pixnet

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=3)
def auto_post():
    try:
        logger.info("開始生成文章...")
        article = generate_article()
        post_to_pixnet(article)
        logger.info("文章發佈成功 ✅")
    except Exception as e:
        logger.error(f"自動發文失敗: {e}")

@app.get("/")
def home():
    return {"status": "running", "message": "PIXNET 自動發文系統已啟動"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=port)
