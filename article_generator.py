from datetime import datetime
from typing import List, Dict
import random, textwrap, os
from news_fetcher import fetch_latest_news
from longtail_keywords import get_keywords

FIXED_LINK = os.getenv("FIXED_LINK", "https://lihi.cc/japMO")

CORE_KEYWORD_LINKS = {
    "理債一日便": "https://www.google.com/search?q=理債一日便",
    "債務整合": "https://www.google.com/search?q=債務整合",
    "房貸": "https://www.google.com/search?q=房貸",
    "信用貸款": "https://www.google.com/search?q=信用貸款",
    "轉貸": "https://www.google.com/search?q=房貸轉貸",
}

def _linkify_core(text: str) -> str:
    for kw, url in CORE_KEYWORD_LINKS.items():
        text = text.replace(kw, f"[{kw}]({url})")
    return text

def _pad_to_length(s: str, target: int = 2000) -> str:
    if len(s) >= target:
        return s
    filler = """
    ### 延伸：總額試算的兩個眉角
    - 別只看利率，要把手續費、違約金、規費換成金額加總。
    - 做利率敏感度測試（±0.25%）去看月付與總額差異。
    """
    while len(s) < target:
        s += "\n" + textwrap.dedent(filler).strip() + "\n"
    return s

def _news_section(news: List[Dict]) -> str:
    lines = ["### 今日新聞精選"]
    for i, n in enumerate(news, 1):
        src = n.get("source","")
        img = n.get("image","")
        line = f"{i}. **{n['title']}**（{src}） → {n['url']}"
        if img:
            line += f"\n\n<p><img src=\"{img}\" alt=\"{n['title']}\" style=\"max-width:100%;height:auto;border-radius:12px\"/></p>"
        lines.append(line)
    return "\n\n".join(lines)

def _linkify_longtails(block: str, kws: List[str]) -> str:
    for kw in sorted(set(kws), key=len, reverse=True):
        safe_kw = kw.replace("[", "\[").replace("]", "\]")
        block = block.replace(kw, f"[{safe_kw}]({FIXED_LINK})")
    return block

def generate_article():
    today = datetime.now().strftime("%Y/%m/%d")
    news = fetch_latest_news(5)
    longtails  = get_keywords(15)

    title = f"理債一日便｜{today} 房市與債務整合重點整理（含長尾關鍵字）"

    intro = (
        "近年利率震盪、房貸族現金流吃緊，「整合負債、轉貸降息、善用寬限期」成為日常議題。"
        "本文彙整今日新聞、理債心法與長尾關鍵字 QA，幫你一次弄懂。"
    )

    news_block = _news_section(news)

    teach = """
    ### 三步驟檢視你的負債結構
    1) 盤點：列出所有貸款（利率/餘額/期數/月付）。  
    2) 試算：把總費用換成年化總成本，比較整合前後**總還款額**與**月現金流**。  
    3) 執行：多比較 2~3 家方案，確認違約期與提前清償費。"""

    random.shuffle(longtails)
    qa_lines = ["### 長尾關鍵字 QA"]
    for kw in longtails:
        q = f"**Q：{kw}？**"
        a = (
            f"A：{kw} 牽涉費用與審核條件，建議先用**總額**做比較，再看是否影響聯徵與後續申貸。"
            "如需進一步諮詢，請參考文內連結。"
        )
        qa_lines.append(q + "\n" + a)
    qa_block = "\n\n".join(qa_lines)

    action = """
    ### 行動清單
    - 先做「債務總表」：利率 / 餘額 / 月付  
    - 比三個方案：維持現況／整合負債／房貸轉貸  
    - 談利率三準備：穩定收入、良好繳款、較低負債比"""

    content = "\n\n".join([intro, news_block, teach, qa_block, action])
    content = _linkify_core(content)
    content = _linkify_longtails(content, longtails)
    content = _pad_to_length(content, 2000)

    tags = ["理債一日便","債務整合","房貸","轉貸","信用貸款"] + longtails[:5]

    return {
        "title": title,
        "content": content,
        "tags": tags,
        "news_used": [{"title":n["title"], "source":n.get("source",""), "url":n["url"], "image":n.get("image","")} for n in news],
        "fixed_link": FIXED_LINK
    }
