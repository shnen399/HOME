import os
import re
from datetime import datetime
from typing import List, Dict

# 兩種來源：環境變數優先、否則退回檔案
ENV_VAR_NAME = "PANEL_ACCOUNTS"                         # 你在 Render 設的變數
ACCOUNTS_FILE = os.getenv("PIXNET_ACCOUNTS_FILE", "pixnet_accounts.txt")

RECORD_FILE = "發文紀錄.txt"

_email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _normalize_line(line: str) -> str:
    # 去掉註解與多餘空白
    line = line.strip()
    if not line or line.startswith("#"):
        return ""
    # 有些人會用中文冒號或空白，統一成 email:password
    line = line.replace("：", ":")
    line = re.sub(r"\s+", "", line)
    return line

def _parse_accounts_text(text: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    for raw in text.splitlines():
        line = _normalize_line(raw)
        if not line:
            continue
        if ":" not in line:
            # 容錯：若貼成 email password，中間空白，前面已移除空白；因此此情況忽略
            continue
        email, pwd = line.split(":", 1)
        if not email or not pwd:
            continue
        if not _email_re.match(email):
            continue
        key = (email, pwd)
        if key in seen:
            continue
        seen.add(key)
        out.append({"email": email, "password": pwd})
    return out

def read_accounts() -> List[Dict[str, str]]:
    """
    讀帳密：
    1) 先讀環境變數 PANEL_ACCOUNTS（每行一組 `email:password`）
    2) 如果沒設或是空的，再讀檔案 ACCOUNTS_FILE（預設 pixnet_accounts.txt）
    """
    env_text = os.getenv(ENV_VAR_NAME, "").strip()
    if env_text:
        accounts = _parse_accounts_text(env_text)
        print(f"[accounts] Loaded {len(accounts)} accounts from env {ENV_VAR_NAME}")
        if accounts:
            return accounts

    # fallback：讀檔
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                text = f.read()
            accounts = _parse_accounts_text(text)
            print(f"[accounts] Loaded {len(accounts)} accounts from file {ACCOUNTS_FILE}")
            return accounts
    except Exception as e:
        print(f"[accounts] Failed to read file {ACCOUNTS_FILE}: {e}")

    print("[accounts] No accounts found (env/file both empty).")
    return []

def append_record(text: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(RECORD_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {text}\n")
    except Exception as e:
        print(f"[record] write failed: {e}")
