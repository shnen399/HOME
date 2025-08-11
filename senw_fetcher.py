import time, requests, xml.etree.ElementTree as ET
from typing import List, Dict
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

# 既有來源
RSS_SOURCES = [
    "https://house.udn.com/rssfeed/news/1002/7225/7295?ch=udn",
    "https://www.chinatimes.com/rss/realtimenews-money.xml?chdtv",
    "https://www.chinatimes.com/rss/real-estate.xml?chdtv",
]

# ➕ 新增：Google 新聞 RSS（以關鍵字搜尋）
# 可自行調整關鍵字；已聚焦房市/貸款/整合等
GOOGLE_NEWS_SEARCH = (
    "房市 OR 房貸 OR 信用貸款 OR 債務整合 OR 轉貸"
)
GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?"
    f"q={quote_plus(GOOGLE_NEWS_SEARCH)}"
    "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
)

HEADERS = {"User-Agent": "Mozilla/5.0"}

def _get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""

def _try_get_image(url: str) -> str:
    try:
        html = requests.get(url, timeout=8, headers=HEADERS).text
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
    """一般 RSS 解析（會直接用 <link> 當最終網址）"""
    items = []
    try:
        res = requests.get(url, timeout=10, headers=HEADERS)
        res.raise_for_status()
        root = ET.fromstring(res.content)
        for it in root.findall(".//item"):
            title = (it.findtext("title") or "").strip()
            link  = (it.findtext("link") or "").strip()
            if not title or not link:
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

def _resolve_google_link(link: str) -> str:
    """
    Google News RSS 的 <link> 多半是 news.google.com/articles/...，
    用 requests 允許跳轉拿到最終原站網址。
    """
    try:
        r = requests.get(link, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.url and "news.google.com" not in _get_domain(r.url):
            return r.url
    except Exception:
        pass
    return link  # 失敗就退回原始連結

def _fetch_google_news() -> List[Dict]:
    items = []
    try:
        res = requests.get(GOOGLE_NEWS_RSS, timeout=10, headers=HEADERS)
        res.raise_for_status()
        root = ET.fromstring(res.content)
        for it in root.findall(".//item"):
            raw_title = (it.findtext("title") or "").strip()
            raw_link  = (it.findtext("link") or "").strip()
            if not raw_title or not raw_link:
                continue
            final_url = _resolve_google_link(raw_link)
            items.append({
                "title": raw_title,
                "url": final_url,
                "source": _get_domain(final_url) or "news.google.com",
                "image": _try_get_image(final_url)
            })
    except Exception:
        pass
    return items

def fetch_latest_news(max_items: int = 5) -> List[Dict]:
    bag: List[Dict] = []

    # 1) 一般 RSS
    for u in RSS_SOURCES:
        bag.extend(_fetch_rss(u))
        time.sleep(0.5)

    # 2) ➕ Google 新聞 RSS
    bag.extend(_fetch_google_news())

    # 如果都抓不到，給保底
    if not bag:
        bag = [
            {"title":"央行關注房市量縮價撐","url":"https://example.com/a1","source":"example.com","image":""},
            {"title":"整合信貸怎麼比費用","url":"https://example.com/a2","source":"example.com","image":""},
        ]

    # 去重（以標題為準），保留前 max_items
    seen = set(); out=[]
    for n in bag:
        t = n.get("title","").strip()
        if not t or t in seen:
            continue
        out.append(n); seen.add(t)
        if len(out) >= max_items:
            break
    return out
