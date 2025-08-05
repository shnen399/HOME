
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from article_generator import generate_article
from utils import post_to_pixnet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=3)
def auto_post():
    try:
        logger.info("開始生成文章...")
        article = generate_article()

        logger.info("準備發佈到 PIXNET...")
        post_to_pixnet(article)

        logger.info("文章發佈成功 ✅")
    except Exception as e:
        logger.error(f"自動發文失敗: {e}")

if __name__ == "__main__":
    logger.info("🔄 自動發文排程器啟動中...")
    scheduler.start()
