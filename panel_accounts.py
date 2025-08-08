import json
import os

FAILED_COUNT_FILE = "login_failed_count.json"
ACCOUNTS_FILE = "自動發文主帳號.txt"

def load_accounts():
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return [tuple(line.strip().split(":")) for line in f if ":" in line]

def mark_failed_login(email):
    if os.path.exists(FAILED_COUNT_FILE):
        with open(FAILED_COUNT_FILE, "r") as f:
            failed_counts = json.load(f)
    else:
        failed_counts = {}

    failed_counts[email] = failed_counts.get(email, 0) + 1

    if failed_counts[email] >= 3:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                if not line.startswith(email):
                    f.write(line)

    with open(FAILED_COUNT_FILE, "w") as f:
        json.dump(failed_counts, f, ensure_ascii=False, indent=2)
