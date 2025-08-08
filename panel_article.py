import random, time
from fastapi.responses import JSONResponse
from article_generator import generate_article
from longtail_keywords import generate_keywords_with_links
from panel_accounts import load_accounts, mark_failed_login
from post_to_pixnet import post_to_pixnet
from line_notify import send_line_notify

def post_article_job():
    accounts = load_accounts()
    for email, password in accounts:
        article = generate_article()
        keywords = generate_keywords_with_links()
        success, response = post_to_pixnet(email, password, article, keywords)
        if success:
            with open("發文紀錄.txt", "a", encoding="utf-8") as f:
                f.write(f"{email} 成功發文：{response}\n")
            send_line_notify(f"✅ 發文成功\n帳號：{email}\n連結：{response}")
            return JSONResponse(content={"status": "success", "account": email})
        else:
            mark_failed_login(email)
    return JSONResponse(content={"status": "failed", "reason": "無可用帳號"})
