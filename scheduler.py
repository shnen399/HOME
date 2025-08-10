import logging
from apscheduler.schedulers.background import BackgroundScheduler
from panel_article import post_article_once

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
log = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Taipei")

def _job():
    try:
        res = post_article_once()
        log.info("自動發文結果：%s", res)
    except Exception as e:
        log.exception("自動發文錯誤：%s", e)

def start_scheduler():
    try:
        scheduler.add_job(_job, "interval", minutes=3, id="auto_post", replace_existing=True)
        scheduler.start()
        log.info("Scheduler 啟動完成（每 3 分鐘執行一次）。")
    except Exception as e:
        log.exception("啟動排程失敗：%s", e)
