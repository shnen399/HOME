from datetime import datetime
import json
LOG_FILE = "發文紀錄.txt"
def append_log(entry: dict):
    entry["ts"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
