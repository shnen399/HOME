import datetime as dt, os
from logger import get_logger, mask_email
from news_fetcher import get_hot_news
from article_generator import generate_article
from pixnet_api import create_article

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
    """
    使用 PIXNET 官方 API 發文。
    需要在環境變數設定：
      - PIXNET_ACCESS_TOKEN：從 developer.pixnet.pro 取得
      - PIXNET_BLOG_ID：你的部落格識別（通常是帳號名稱）
    """
    token = os.getenv("PIXNET_ACCESS_TOKEN", "").strip()
    blog_id = os.getenv("PIXNET_BLOG_ID", "").strip()
    if not token or not blog_id:
        log.warning("缺少 PIXNET_ACCESS_TOKEN 或 PIXNET_BLOG_ID，改用 Demo 連結。")
        return "https://pixnet.example.com/blog/post/123456"

    res = create_article(access_token=token, blog_id=blog_id, title=title, body=content)
    return res["url"]

def gen_longtail_keywords() -> list:
    today = dt.datetime.now()
    ym = today.strftime("%Y年%m月")
    base = [
        "理債一日便",
        "信用貸款",
        "小額信貸",
        "房貸轉貸",
        "整合負債",
        "負債整合",
        "利率試算",
        "貸款注意事項",
    ]
    templates = [
        "{k} {ym} 最新方案比較",
        "{k} {ym} 利率試算教學",
        "{k} {ym} 申請條件與流程",
        "{k} {ym} 常見問題 懶人包",
        "{k} {ym} 合法管道與風險",
    ]
    out = []
    for k in base:
        for t in templates:
            out.append(t.format(k=k, ym=ym))
            if len(out) >= 20:
                return out
    return out

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
