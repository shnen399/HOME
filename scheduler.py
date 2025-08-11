from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core import post_article_once

_sched = BackgroundScheduler()
_started = False

def start_scheduler():
    global _started
    if _started:
        return
    # 每 3 分鐘跑一次；避免重複排相同 ID
    _sched.add_job(
        post_article_once,
        trigger=IntervalTrigger(minutes=3),
        id="auto_post",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )
    _sched.start()
    _started = True
