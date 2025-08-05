
import random
import datetime
import requests
from bs4 import BeautifulSoup

# 讀取外部資料
def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

AFFILIATE_ARTICLES = read_file('affiliate_articles.txt')
LONGTAIL_KEYWORDS = read_file('longtail_keywords.txt')
TAGS = read_file('tags.txt')

NEWS_SOURCES = [
    "https://tw.news.yahoo.com/",
    "https://today.line.me/tw/v2/tab/top",
    "https://www.ettoday.net/news/focus/%E6%96%B0%E8%81%9E/",
    "https://newtalk.tw/news/summary"
]

def fetch_news():
    news_list = []
    for url in NEWS_SOURCES:
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'lxml')
            for a in soup.find_all('a')[:3]:  # 每來源抓取前 3 則
                title = a.get_text().strip()
                link = a.get('href')
                if title and link:
                    news_list.append((title, link))
        except:
            continue
    return news_list

def generate_article():
    news = fetch_news()
    selected_news = random.choice(news) if news else ("今日新聞", "#")

    affiliate_text = random.choice(AFFILIATE_ARTICLES) if AFFILIATE_ARTICLES else ""
    longtail_kw = random.choice(LONGTAIL_KEYWORDS) if LONGTAIL_KEYWORDS else ""

    tags_html = ""
    for tag in TAGS:
        parts = tag.split("|")
        if len(parts) == 2:
            tags_html += f"<a href='{parts[1]}' target='_blank'>#{parts[0]}</a> "
        else:
            tags_html += f"#{parts[0]} "

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"{selected_news[0]} - {longtail_kw}"
    content = f"{affiliate_text}\n\n來源新聞：<a href='{selected_news[1]}'>{selected_news[0]}</a>\nSEO關鍵字：{longtail_kw}\n發布時間：{date}\n\n標籤：{tags_html}"

    article = {
        "title": title,
        "content": content,
        "tags": [longtail_kw, "自動發文", "新聞"]
    }
    return article
