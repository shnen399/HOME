import os, requests

def send_line_notify(message: str):
    token = os.getenv("LINE_NOTIFY_TOKEN")
    if not token:
        return
    try:
        requests.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {token}"},
            data={"message": message},
            timeout=15
        )
    except Exception:
        pass
