from article_generator import generate_article
from logger import append_log
from utils import read_accounts
from line_notify import send_line_notify

BAD_LIST = "bad_accounts.txt"
FAIL_COUNT = {}

try:
    from post_to_pixnet import pixnet_login_and_post
except Exception:
    def pixnet_login_and_post(user, pwd, title, content, tags):
        raise RuntimeError("請在 post_to_pixnet.py 實作 pixnet_login_and_post(user, pwd, title, content, tags)")

def _mark_bad(username: str):
    with open(BAD_LIST, "a", encoding="utf-8") as f:
        f.write(username + "\n")

def post_article_once():
    article = generate_article()
    accounts = read_accounts()
    results = []

    for acc in accounts:
        user = acc["email"]; pwd = acc["password"]
        try:
            ok, info = pixnet_login_and_post(user, pwd, article["title"], article["content"], article["tags"])
            if ok:
                append_log({
                    "account": user,
                    "status": "success",
                    "title": article["title"],
                    "post_url": info,
                    "news_used": article["news_used"]
                })
                send_line_notify(f"✅ 發文成功 | {user} | {article['title']}\n{info}")
                FAIL_COUNT[user] = 0
                results.append({"account": user, "ok": True, "url": info})
            else:
                raise RuntimeError(info or "發文失敗")
        except Exception as e:
            FAIL_COUNT[user] = FAIL_COUNT.get(user, 0) + 1
            append_log({
                "account": user,
                "status": "fail",
                "title": article["title"],
                "error": str(e)
            })
            send_line_notify(f"❌ 發文失敗({FAIL_COUNT[user]}) | {user} | {article['title']}\n原因: {e}")
            results.append({"account": user, "ok": False, "error": str(e)})
            if FAIL_COUNT[user] >= 3:
                _mark_bad(user)

    return {"title": article["title"], "results": results}
