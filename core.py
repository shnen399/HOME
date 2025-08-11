# DEMO 版：保證輸出關鍵字到 Logs 與紀錄
import datetime as dt
from logger import get_logger, mask_email
from news_fetcher import get_hot_news
from article_generator import generate_article

log = get_logger("core")

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
    # TODO: 接回你的真實發文函式（此處先回 demo 連結）
    return "https://pixnet.example.com/blog/post/123456"

def gen_longtail_keywords():
    return [
        "理債方案比較 2025 最新懶人包",
        "信用貸款利率試算教學 步驟解析",
        "小額信貸常見問題 與申請重點",
        "房貸轉貸成本 試算與流程指南",
        "整合負債注意事項 合法管道推薦",
    ]

def post_article_once(accounts_file="panel_accounts.txt"):
    news = get_hot_news(limit=3)
    keywords = gen_longtail_keywords()
    log.info("本次長尾關鍵字：%s", "、".join(keywords))

    article = generate_article(news, keywords)
    title, content = article["title"], article["content"]

    email, pwd = pick_account(accounts_file)
    masked = mask_email(email)
    log.info("準備用帳號發文：%s，標題：%s", masked, title)

    url = real_pixnet_post(email, pwd, title, content)

    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_str = "；".join([f"{n['source']}|{n['title']}|{n['url']}" for n in news])
    kw_str  = "；".join(keywords)
    with open("發文紀錄.txt", "a", encoding="utf-8") as f:
        f.write(f"{ts} | 帳號={masked} | 標題={title} | 文章連結={url} | 關鍵字={kw_str} | 來源={src_str}\n")
    with open("關鍵字紀錄.txt", "a", encoding="utf-8") as f:
        f.write(f"{ts} | {kw_str}\n")

    log.info("發文成功：%s", url)
    return {"ok": True, "url": url, "title": title, "account": masked, "keywords": keywords}
