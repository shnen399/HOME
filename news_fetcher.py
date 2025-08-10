import time, requests, xml.etree.ElementTree as ET
from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

RSS_SOURCES = [
    "https://house.udn.com/rssfeed/news/1002/7225/7295?ch=udn",
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
            return og["content"]
        img = soup.find("img", src=True)
        if img:
            return img["src"]
    except Exception:
        pass
    return ""

def _fetch_rss(url: str) -> List[Dict]:
    items = []
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        res.raise_for_status()
        root = ET.fromstring(res.content)
        for it in root.findall(".//item"):
            title = (it.findtext("title") or "").strip()
            link  = (it.findtext("link") or "").strip()
            if not title:
                continue
            items.append({
                "title": title,
                "url": link,
                "source": _get_domain(link),
                "image": _try_get_image(link)
            })
    except Exception:
        pass
    return items

def fetch_latest_news(max_items: int = 5) -> List[Dict]:
    bag: List[Dict] = []
    for u in RSS_SOURCES:
        bag.extend(_fetch_rss(u))
        time.sleep(0.5)
    if not bag:
        bag = [
            {"title":"央行關注房市量縮價撐","url":"https://example.com/a1","source":"example.com","image":""},
            {"title":"整合信貸怎麼比費用","url":"https://example.com/a2","source":"example.com","image":""},
        ]
    seen = set(); out=[]
    for n in bag:
        if n["title"] in seen: 
            continue
        out.append(n); seen.add(n["title"])
        if len(out) >= max_items: 
            break
    return out
