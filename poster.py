# poster.py — 覆蓋版
import os
import re
from urllib.parse import urlparse

def _looks_like_real_pixnet_url(url: str) -> bool:
    """
    確認是不是痞客邦的「實際文章連結」
    規則：scheme http/https、網域結尾 .pixnet.net、path 內含 /post 或 /blog/post
    """
    try:
        u = urlparse(url)
        if u.scheme not in ("http", "https"):
            return False
        host = (u.netloc or "").lower()
        if not host.endswith(".pixnet.net"):
            return False
        path = (u.path or "").lower()
        return ("/post" in path) or ("/blog/post" in path)
    except Exception:
        return False


def post_once(email: str, password: str, title: str, content: str, tags):
    """
    封裝發文流程：
    - 優先使用既有的 post_to_pixnet.pixnet_login_and_post（你專案裡已在用）
    - 成功一定回傳 (True, <真實文章URL>)
    - 若回來的是範例網址或奇怪的東西，改回 (False, <說明>)
    """
    # 先嘗試呼叫舊的實作
    try:
        from post_to_pixnet import pixnet_login_and_post  # type: ignore
    except Exception as e:
        return False, f"找不到發文實作 post_to_pixnet.pixnet_login_and_post：{e}"

    ok, result = pixnet_login_and_post(email, password, title, content, tags)

    if not ok:
        return False, f"發文失敗：{result}"

    url = str(result).strip()

    # 擋掉常見的「範例」或假連結
    bad_examples = (
        "ixnet.example.com",   # 之前看到的示範網址
        "example.com",
        "localhost",
    )
    if any(b in url for b in bad_examples):
        return False, f"發文後未取得實際連結（得到範例網址：{url}）。請檢查登入/發文流程。"

    if not _looks_like_real_pixnet_url(url):
        return False, f"發文回傳非預期的連結：{url}。請確認是否已成功登入並建立文章。"

    # 一切正常：回傳真實文章 URL
    return True, url
