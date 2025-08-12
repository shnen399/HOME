# main.py  — 覆蓋版

import os
import json
import traceback
from typing import Tuple, List, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

# 可選：若專案內有 scheduler.start_scheduler()，就啟用；沒有也不會壞
try:
    from scheduler import start_scheduler  # type: ignore
except Exception:
    start_scheduler = None  # 沒有就略過

app = FastAPI(
    title="PIXNET 自動海報",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 啟動背景排程（如果有）
if start_scheduler:
    try:
        start_scheduler()
    except Exception:
        pass


# ---------- 小工具 ----------

def _read_accounts_from_env() -> List[Tuple[str, str]]:
    """
    從環境變數 PIXNET_ACCOUNTS 讀帳密，多行，每行 email:password
    """
    raw = os.getenv("PIXNET_ACCOUNTS", "").strip()
    out: List[Tuple[str, str]] = []
    if not raw:
        return out
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        email, pwd = line.split(":", 1)
        out.append((email.strip(), pwd.strip()))
    return out


def _read_accounts_from_file(file_name: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    if not os.path.exists(file_name):
        return out
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            email, pwd = line.split(":", 1)
            out.append((email.strip(), pwd.strip()))
    return out


def pick_account() -> Tuple[str, str]:
    """
    依序嘗試：環境變數 → panel_accounts.txt → pixnet_accounts.txt
    取第一組帳密。
    """
    for src in (
        _read_accounts_from_env(),
        _read_accounts_from_file("panel_accounts.txt"),
        _read_accounts_from_file("pixnet_accounts.txt"),
    ):
        if src:
            return src[0]
    raise RuntimeError("找不到 PIXNET 帳密。請設定環境變數 PIXNET_ACCOUNTS 或提供 panel_accounts.txt / pixnet_accounts.txt。")


def get_article() -> Tuple[str, str, List[str]]:
    """
    取得要發的 〈標題, 內容HTML, 標籤清單〉
    若存在 article_generator.generate_article() 則使用；
    否則用簡易範本。
    """
    try:
        from article_generator import generate_article  # type: ignore
        data = generate_article()
        title = data.get("title") or "自動發文：測試標題"
        content = data.get("content") or "<p>這是自動產生的測試內文。</p>"
        tags = data.get("tags") or ["自動", "測試"]
        if not isinstance(tags, list):
            tags = ["自動", "測試"]
        return title, content, tags  # type: ignore
    except Exception:
        # 後備方案
        return (
            "自動發文：測試標題",
            "<h2>測試內文</h2><p>這是後備內文，代表你的 article_generator 還沒就緒。</p>",
            ["自動", "測試"],
        )


def _post_via_poster(email: str, password: str, title: str, content: str, tags: List[str]) -> Tuple[bool, str]:
    """
    優先呼叫 poster.post_once(email, password, title, content, tags) -> (ok, result)
    沒有 poster 模組時，退回 post_to_pixnet.pixnet_login_and_post(...)
    """
    try:
        from poster import post_once  # type: ignore
        ok, result = post_once(email, password, title, content, tags)
        return bool(ok), str(result)
    except Exception:
        # 改用舊介面
        try:
            from post_to_pixnet import pixnet_login_and_post  # type: ignore
            ok, result = pixnet_login_and_post(email, password, title, content, tags)
            return bool(ok), str(result)
        except Exception as e2:
            return False, f"無法發文：{e2}\n{traceback.format_exc()}"


# ---------- 路由 ----------

@app.get("/", response_class=JSONResponse)
def root():
    return {
        "message": "服務正常運行中",
        "hint": "到 /docs 打開 Swagger，按 POST /post_article 測試發文",
    }


@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "OK: True"


@app.post("/post_article", response_class=JSONResponse)
def post_article():
    """
    發一篇文章到痞客邦：
    1) 取帳號密碼（env 或檔案）
    2) 生成文章（article_generator 如有）
    3) 透過 poster 或 post_to_pixnet 發文
    4) 回傳 success / fail 與細節；例外則附上 trace
    """
    try:
        email, password = pick_account()
        title, content, tags = get_article()

        ok, result = _post_via_poster(email, password, title, content, tags)

        if ok:
            return {"status": "success", "url": result, "title": title, "tags": tags[:5]}
        else:
            return {"status": "fail", "error": result, "title": title, "tags": tags[:5]}
    except Exception as e:
        return {
            "status": "error",
            "exception": str(e),
            "trace": traceback.format_exc(),
        }
