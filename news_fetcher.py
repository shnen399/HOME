
# REAL 版：抓多個 RSS 來源（盡量避開被擋），並寫入紀錄 + Logs
from typing import List, Dict
import xml.etree.ElementTree as ET
import requests, datetime as dt
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from logger import get_logger

log = get_logger("news")

# 可自行增刪來源（盡量放 RSS 以避免 Cloudflare 防護頁）
RSS_SOURCES = [
    # UDN 財經
    "https://www.udn.com/rssfeed/news/1/6/1002?ch=udn",
    # 中時即時財經/房市
    "https://www.chinatimes.com/rss/realtimenews-money.xml?chdtv",
    "https://www.chinatimes.com/rss/real-estate.xml?chdtv",
]

UA = {"User-Agent": "Mozilla/5.0 (compatible; PixnetAutoPoster/1.0)"}

def _get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""

def _try_get_image(url: str) -> str:
    # 非必要，抓 og:image 當配圖
    try:
        html = requests.get(url, timeout=10, headers=UA).text
        soup = BeautifulSoup(html, "lxml")
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if og and og.get("content"):
            return og.get("content")
    except Exception:
        pass
    return ""

def _fetch_rss(url: str) -> List[Dict]:
    items: List[Dict] = []
    r = requests.get(url, timeout=12, headers=UA)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not title or not link:
            continue
        items.append({
            "title": title,
            "url": link,
            "source": _get_domain(link) or _get_domain(url),
            "image": "",
        })
    return items

def get_hot_news(limit: int = 3) -> List[Dict]:
    all_items: List[Dict] = []
    for rss in RSS_SOURCES:
        try:
            all_items.extend(_fetch_rss(rss))
        except Exception as e:
            log.warning(f"抓取 {rss} 失敗: {e}")
    # 去重
    seen = set()
    uniq: List[Dict] = []
    for it in all_items:
        u = it["url"]
        if u not in seen:
            seen.add(u)
            uniq.append(it)
        if len(uniq) >= limit:
            break

    # 紀錄
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("新聞紀錄.txt", "a", encoding="utf-8") as f:
        for it in uniq:
            line = f"{ts} | {it['source']} | {it['title']} | {it['url']}"
            f.write(line + "\n")
            log.info(line)
    log.info(f"抓到新聞 {len(uniq)} 則（REAL）")
    return uniq
