# main.py — 修正版（可直接覆蓋）

import os
import traceback
import logging
from typing import Tuple, List

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

# 可選：若專案內有 scheduler.start_scheduler()，就啟用；沒有也不會壞
try:
    from scheduler import start_scheduler  # type: ignore
except Exception:
    start_scheduler = None  # 沒有就略過

# ====== 日誌設定 ======
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("core")

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
        log.exception("排程啟動失敗（略過）")


# ---------- 小工具 ----------

def _read_accounts_from_env() -> List[Tuple[str, str]]:
    """從環境變數 PIXNET_ACCOUNTS 讀帳密，多行，每行 email:password"""
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
        # 後備方案（內容改用三引號，避免 SyntaxError）
        return (
            "自動發文：測試標題",
            """<h2>測試內文</h2><p
