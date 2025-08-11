import os, re, json, sqlite3
from datetime import datetime
from typing import List, Tuple, Dict
import feedparser

FIXED_LINK = os.getenv("FIXED_LINK","https://lihi.cc/japMO")
DB_PATH = "data.db"
TEXT_LOG = "發文紀錄.txt"

NEWS_FEEDS = [
    "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    "https://news.google.com/rss/search?q=%E8%B2%A1%E7%B6%93&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    "https://tw.news.yahoo.com/rss",
    "https://feeds.feedburner.com/ettoday/finance",
    "https://newtalk.tw/rss/cat/finance"
]

def ensure_db():
    con = sqlite3.connect(DB_PATH); cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, account TEXT, title TEXT, status TEXT, url TEXT, error TEXT)")
    con.commit(); con.close()

def add_log_row(ts: str, account: str, title: str, status: str, info: str = ""):
    with open(TEXT_LOG,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":ts,"account":account,"title":title,"status":status,"info":info}, ensure_ascii=False)+"\n")
    con = sqlite3.connect(DB_PATH); cur = con.cursor()
    if status=="success":
        cur.execute("INSERT INTO logs(ts,account,title,status,url,error) VALUES(?,?,?,?,?,?)",(ts,account,title,status,info,""))
    else:
        cur.execute("INSERT INTO logs(ts,account,title,status,url,error) VALUES(?,?,?,?,?,?)",(ts,account,title,status,"",info))
    con.commit(); con.close()

def get_logs(limit: int=100):
    con = sqlite3.connect(DB_PATH); cur = con.cursor()
    cur.execute("SELECT ts,account,title,status,url,error FROM logs ORDER BY id DESC LIMIT ?",(limit,))
    rows = cur.fetchall(); con.close()
    return [{"ts":r[0],"account":r[1],"title":r[2],"status":r[3],"url":r[4],"error":r[5]} for r in rows]

def fetch_news(max_items=3):
    items=[]
    for feed in NEWS_FEEDS:
        d = feedparser.parse(feed)
        for e in d.entries[:5]:
            t = e.get("title","").strip(); l = e.get("link","").strip()
            if t and l: items.append({"title":t,"link":l})
        if len(items)>=max_items: break
    return items[:max_items]

def long_tail(topic: str, n=14):
    base=[f"{topic} 貸款整合試算", f"{topic} 提升核貸機率", f"{topic} 高利率現金流管理", f"{topic} 二胎房貸風險", f"{topic} 信用評分快速補救", f"{topic} 月付壓力解法", f"{topic} 轉貸降息教學", f"{topic} 拒貸替代方案", f"{topic} 整合負債省息", f"{topic} 小額信貸循環差異", f"{topic} 聯徵影響與修復", f"{topic} 申貸資料清單", f"{topic} 現金流預算模板", f"{topic} 債務雪球停止法"]
    return [b if len(b)>=18 else b+" 懶人包" for b in base[:n]]

def wrap_links(kw: List[str]) -> str:
    return "｜".join([f'<a href="{FIXED_LINK}" target="_blank" rel="nofollow">{k}</a>' for k in kw])

def generate_article():
    news = fetch_news()
    topic = news[0]["title"] if news else "理債一日便"
    title = (f"理債一日便｜{topic}｜{datetime.now().strftime('%Y/%m/%d %H:%M')}")[:80]
    kw = long_tail(topic, n=14)
    src = "<ul>" + "".join([f'<li><a href="{n["link"]}" target="_blank" rel="noopener">{n["title"]}</a></li>' for n in news]) + "</ul>" if news else ""
    blocks = [
      f"<p><strong>導言</strong>：{topic} 最新焦點，本文提供現金流盤點與債務整合實務操作。</p>",
      "<h3>一、現金流盤點</h3><p>列出收入與支出，計算月結餘，優先保護現金流。</p>",
      "<h3>二、整合前的資料表</h3><p>餘額、利率、期數、月付、違約金、帳管費，計算等效年成本。</p>",
      "<h3>三、核貸視角</h3><p>銀行看穩定收入、負債比、信用紀錄、擔保品。</p>",
      "<h3>四、案例演練</h3><p>由多筆高利負債整合為單筆中低利，月付降低現金流轉正。</p>",
      "<h3>五、QA</h3><p>信用不好先改善紀律與繳款，避免多頭申貸。</p>",
      src,
      f"<p><strong>延伸關鍵字：</strong>{wrap_links(kw)}</p>"
    ]
    content = "\n".join(blocks) + "<p>補充說明：" + ("重點在總成本思維與現金流優先。" * 120) + "</p>"
    return title, content, kw
