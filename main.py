# main.py — 一檔搞定：健康檢查 + 發文 API（讀帳號→生文→發文→回傳網址）

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
import os, random

# 這兩個檔案你已經有了
from article_generator import generate_article
from post_to_pixnet import pixnet_login_and_post


app = FastAPI(
    title="PIXNET 自動海報",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# --------- 帳號讀取工具 ---------
def _parse_accounts(text: str):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        email, pwd = line.split(":", 1)
        email, pwd = email.strip(), pwd.strip()
        if email and pwd:
            out.append({"email": email, "password": pwd})
    return out


def read_accounts():
    """
    讀取帳號的優先序：
    1) 環境變數 PIXNET_ACCOUNTS（格式：email:pwd|email2:pwd2）
    2) 專案根目錄 panel_accounts.txt
    3) 專案根目錄 pixnet_accounts.txt
    """
    # 1) env
    env_accounts = os.getenv("PIXNET_ACCOUNTS", "").strip()
    if env_accounts:
        return _parse_accounts(env_accounts.replace("|", "\n"))

    # 2) panel_accounts.txt
    for fn in ("panel_accounts.txt", "pixnet_accounts.txt"):
        if os.path.exists(fn):
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    return _parse_accounts(f.read())
            except Exception:
                pass

    return []


def pick_account():
    accs = read_accounts()
    if not accs:
        return None
    return random.choice(accs)


# --------- 路由 ---------
@app.get("/", response_class=PlainTextResponse)
def root():
    return "服務正常運行中。到 /docs -> POST /post_article 可立即測試發文。"


@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "OK"


@app.post("/post_article")
def post_article():
    try:
        acc = pick_account()
        if not acc:
            return JSONResponse(
                {
                    "status": "fail",
                    "message": "找不到帳號。請在 panel_accounts.txt 或 pixnet_accounts.txt 放入 email:password（或設定環境變數 PIXNET_ACCOUNTS）。",
                },
                status_code=400,
            )

        # 1) 產生文章
        art = generate_article()
        title = art["title"]
        content = art["content"]
        tags = art["tags"]

        # 2) 發文（post_to_pixnet.py 內的函式）
        ok, url_or_err = pixnet_login_and_post(
            acc["email"], acc["password"], title, content, tags
        )

        # 3) 回傳
        if ok:
            return {
                "status": "success",
                "message": "發文成功",
                "url": url_or_err,
                "account": acc["email"],
                "title": title,
                "keywords": tags,
            }
        else:
            return {
                "status": "fail",
                "message": url_or_err,
                "url": "",
                "account": acc["email"],
                "title": title,
                "keywords": tags,
            }

    except Exception as e:
        return JSONResponse(
            {"status": "fail", "message": f"例外錯誤：{e}", "url": ""}, status_code=500
        )
