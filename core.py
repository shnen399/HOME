import datetime as dt, os, json
from typing import List
from logger import get_logger, mask_email
from news_fetcher import get_hot_news
from article_generator import generate_article

log = get_logger("core")
FAIL_FILE = "login_failed_count.json"

# 你原本已有的：挑帳號 / 真實發文函式（這裡放佔位，整合時會用你的版本）
def pick_account(accounts_file="panel_accounts.txt"):
    with open(accounts_file, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line or ":" not in line: 
                continue
            email, pwd = line.split(":", 1)
            return email, pwd
    raise RuntimeError("帳號檔為空")

def real_pixnet_post(email: str, pwd: str, title: str, content: str) -> str:
    # TODO: 用你的發文函式替換並回傳文章連結
    return "https://example.pixnet.net/blog/post/123456"

def _load_fail():
    if os.path.exists(FAIL_FILE):
        return json.load(open(FAIL_FILE, "r", encoding="utf-8"))
    return {}

def _save_fail(data):
    json.dump(data, open(FAIL_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def post_article_once(accounts_file="panel_accounts.txt"):
    # 1) 抓新聞 + 紀錄
    news = get_hot_news(limit=3)

    # 2) 生成關鍵字（請換成你的生成器）
    keywords = [
        "理債方案比較 2025 最新",
        "信用貸款利率試算教學",
        "小額信貸注意事項 懶人包",
        "房貸轉貸流程 與成本說明",
    ]
    log.info("本次長尾關鍵字：%s", "、".join(keywords))

    # 3) 產文
    article = generate_article(news, keywords)
    title, content = article["title"], article["content"]

    # 4) 帳號登入 + 發文
    email, pwd = pick_account(accounts_file)
    masked = mask_email(email)
    log.info("準備用帳號發文：%s，標題：%s", masked, title)

    url = real_pixnet_post(email, pwd, title, content)

    # 5) 成功紀錄（含來源與關鍵字）
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_str = "；".join([f"{n['source']}|{n['title']}|{n['url']}" for n in news])
    kw_str  = "；".join(keywords)
    with open("發文紀錄.txt", "a", encoding="utf-8") as f:
        f.write(f"{ts} | 帳號={masked} | 標題={title} | 文章連結={url} | 關鍵字={kw_str} | 來源={src_str}\n")
    with open("關鍵字紀錄.txt", "a", encoding="utf-8") as f:
        f.write(f"{ts} | {kw_str}\n")

    log.info("發文成功：%s", url)
    return {"ok": True, "url": url, "title": title, "account": masked, "keywords": keywords}
