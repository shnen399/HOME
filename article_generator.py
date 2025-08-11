from typing import List, Dict
import textwrap, os

FIXED = os.getenv("FIXED_LINK", "https://lihi.cc/japMO")

def build_kw_block(keywords: List[str]) -> str:
    if not keywords: 
        return ""
    lines = [f"- {k} → {FIXED}" for k in keywords]
    return "\n\n---\n### 熱門長尾關鍵字\n" + "\n".join(lines) + "\n"

def build_sources_block(news: List[Dict]) -> str:
    if not news:
        return ""
    lines = [f"- {n['source']}：{n['title']}（{n['url']}）" for n in news]
    return "\n\n---\n### 參考來源\n" + "\n".join(lines) + "\n"

def generate_article(news: List[Dict], keywords: List[str]) -> Dict:
    # 這裡使用你現有的 2000+ 字生成邏輯；先放一段 placeholder
    body = "（此處接你的長文內容，保持 2000+ 字）"
    content = textwrap.dedent(f"""{body}""").strip()
    content += build_kw_block(keywords)
    content += build_sources_block(news)
    title = news[0]["title"] if news else "理債一日便｜最新趨勢解析"
    return {"title": title, "content": content}
