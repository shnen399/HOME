import os, requests, json
from typing import Optional, List, Dict
from logger import get_logger

log = get_logger("pixnet-api")

API_BASE = "https://emma.pixnet.cc"
CREATE_ARTICLE_URL = f"{API_BASE}/blog/articles"

def _auth_headers(access_token: str) -> dict:
    # PIXNET API 通常接受 query 參數 access_token；但也嘗試 Bearer header
    return {"Authorization": f"Bearer {access_token}", "User-Agent": "PixnetAutoPoster/1.0"}

def create_article(
    access_token: str,
    blog_id: str,
    title: str,
    body: str,
    tags: Optional[List[str]] = None,
    category_id: Optional[int] = None,
) -> Dict:
    """
    呼叫 PIXNET Blog API 建立文章。
    需要：access_token（OAuth2）、blog_id（你的部落格識別，通常等於帳號名稱）。
    參考端點：POST https://emma.pixnet.cc/blog/articles?format=json
    重要：請先到 developer.pixnet.pro 取得 Access Token，放入環境變數 PIXNET_ACCESS_TOKEN。
    """
    params = {"format": "json"}
    data = {
        "title": title,
        "body": body,
        "blog_id": blog_id,
    }
    if tags:
        data["tags"] = ",".join(tags)
    if category_id is not None:
        data["category_id"] = str(category_id)

    # 主要用 Bearer Header；同時帶 query 參數以兼容舊行為
    headers = _auth_headers(access_token)
    params["access_token"] = access_token

    log.info("呼叫 PIXNET 建立文章：blog_id=%s，title=%s", blog_id, title[:40])
    r = requests.post(CREATE_ARTICLE_URL, params=params, data=data, headers=headers, timeout=20)
    try:
        j = r.json()
    except Exception:
        log.warning("PIXNET 回傳非 JSON：%s", r.text[:400])
        r.raise_for_status()
        raise

    if r.status_code >= 400 or "error" in j:
        log.warning("PIXNET API 失敗（%s）：%s", r.status_code, json.dumps(j)[:400])
        raise RuntimeError(j.get("error", {}).get("message", f"HTTP {r.status_code}"))

    # 依 API 結構抓出文章連結（常見欄位：article.link / article.url / article.id）
    art = j.get("article") or j.get("data") or j
    post_url = (
        art.get("link")
        or art.get("url")
        or (f"https://{blog_id}.pixnet.net/blog/post/{art.get('id')}" if art.get("id") else None)
    )
    if not post_url:
        post_url = f"https://{blog_id}.pixnet.net/"
    return {"ok": True, "url": post_url, "raw": j}
