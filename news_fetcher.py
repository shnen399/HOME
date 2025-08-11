# DEMO 版：保證回傳 3 則新聞，並寫入紀錄 + Logs
from typing import List, Dict
import datetime as dt
from logger import get_logger
log = get_logger("news")

def get_hot_news(limit: int = 3) -> List[Dict]:
    demo = [
        {
            "title": "央行釋出最新利率動向，房貸族如何應對？",
            "url": "https://news.example.com/a1",
            "source": "DemoNews"
        },
        {
            "title": "信用貸款比較 2025：手把手教你試算月付",
            "url": "https://news.example.com/a2",
            "source": "DemoNews"
        },
        {
            "title": "小額信貸注意事項：5 個常見坑別踩",
            "url": "https://news.example.com/a3",
            "source": "DemoNews"
        },
    ][:limit]

    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("新聞紀錄.txt", "a", encoding="utf-8") as f:
        for it in demo:
            line = f"{ts} | {it['source']} | {it['title']} | {it['url']}"
            f.write(line + "\n")
            log.info(line)
    log.info(f"抓到新聞 {len(demo)} 則（DEMO）")
    return demo
