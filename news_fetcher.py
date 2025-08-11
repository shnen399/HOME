import time, requests, xml.etree.ElementTree as ET
from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import datetime as dt
from logger import get_logger
log = get_logger("news")

RSS_SOURCES = [
    "https://www.udn.com/rssfeed/news/1002/7225?ch=udn",
    "https://www.chinatimes.com/rss/realtimenews-money.xml?chdtv",
    "https://www.chinatimes.com/rss/real-estate.xml?chdtv",
]

def _get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""

def _try_get_image(url: str) -> str:
    try:
        html = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "lxml")
        og = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name":"og:image"})
        if og and og.get("content"):
            return og.get("content")
        img = soup.find("img", src=True)
        if img:
            return img["src"]
    except Exception:
        pass
    return ""

def fetch_rss(url: str) -> List[Dict]:
    r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src = _get_domain(link) or _get_domain(url)
        items.append({
            "title": title,
            "url": link,
            "source": src,
            "image": _try_get_image(link)
        })
    return items

def get_hot_news(limit=3) -> List[Dict]:
    all_items: List[Dict] = []
    for rss_url in RSS_SOURCES:
        try:
            all_items.extend(fetch_rss(rss_url))
        except Exception as e:
            log.warning(f"抓取 {rss_url} 失敗: {e}")
    # 簡單去重 & 截取
    seen = set()
    uniq = []
    for it in all_items:
        key = it.get("url")
        if key and key not in seen:
            seen.add(key)
            uniq.append(it)
    uniq = uniq[:limit]
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("新聞紀錄.txt", "a", encoding="utf-8") as f:
        for it in uniq:
            line = f"{ts} | {it.get('source','')} | {it.get('title','')} | {it.get('url','')}"
            f.write(line + "\n")
            log.info(line)
    log.info(f"抓到新聞 {len(uniq)} 則")
    return uniq
