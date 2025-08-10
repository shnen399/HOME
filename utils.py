import os
from datetime import datetime
from accounts_embedded import ACCOUNTS as EMBEDDED_ACCOUNTS

ACCOUNTS_FILE = os.getenv("PIXNET_ACCOUNTS_FILE", "pixnet_accounts.txt")
RECORD_FILE = "發文紀錄.txt"

def read_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                email, pwd = line.split(":", 1)
                accounts.append({"email": email.strip(), "password": pwd.strip()})
        if accounts:
            return accounts
    for email, pwd in EMBEDDED_ACCOUNTS:
        accounts.append({"email": email, "password": pwd})
    return accounts

def append_record(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RECORD_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")
