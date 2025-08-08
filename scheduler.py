from apscheduler.schedulers.background import BackgroundScheduler
from panel_article import post_article_job

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(post_article_job, 'interval', seconds=180, id='auto_post')
    scheduler.start()
