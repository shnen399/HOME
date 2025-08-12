# post_to_pixnet.py
# 介面：pixnet_login_and_post(email, password, title, content, tags) -> (bool, str)

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from typing import List, Tuple
import re, time

# === 登入頁 ===
LOGIN_URL = "https://user.pixnet.net/login?service=blog"

# 你提供的 selector（登入）
SEL_LOGIN_EMAIL  = "#signin__form--post > div.signin__section.signin__section-email > input"
SEL_LOGIN_PWD    = 'input[name="password"]'
SEL_LOGIN_SUBMIT = "#signin__form--post > button"

# === 發文頁（面板）===
CANDIDATE_NEW_POST_URLS = [
    "https://panel.pixnet.cc/blog/articles/new",
    "https://panel.pixnet.net/blog/articles/new",
    "https://panel.pixnet.cc/blog/article/new",
    "https://panel.pixnet.net/blog/article/new",
]

# 你提供的 selector（發文）
SEL_TITLE_INPUT   = "#editArticle-header-title"
SEL_PUBLISH_BTN   = "#edit-article-footer > div.action-buttons > button.radius.text-primary.display-at-desktop"
SEL_TAG_INPUT     = "#editArticle-header-tag-input"

# CKEditor 可編輯 body 的定位（自動找 iframe → contenteditable body）
SEL_EDITABLE_BODY = 'body[contenteditable="true"]'


def _fill_ckeditor_frame(page, html: str):
    """
    嘗試尋找 CKEditor 的 iframe，切進去後對 contenteditable 的 body 填入內容。
    若找不到 iframe，退而求其次在同頁面找 contenteditable body。
    """
    # 先試 iframe
    for fr in page.frames:
        try:
            if fr.locator(SEL_EDITABLE_BODY).count() > 0:
                fr.locator(SEL_EDITABLE_BODY).first.fill("")      # 先清空
                fr.locator(SEL_EDITABLE_BODY).first.evaluate(
                    "(el, html) => el.innerHTML = html", html
                )
                return True
        except Exception:
            pass

    # 沒有 iframe，就直接在主頁找
    try:
        if page.locator(SEL_EDITABLE_BODY).count() > 0:
            page.locator(SEL_EDITABLE_BODY).first.fill("")
            page.locator(SEL_EDITABLE_BODY).first.evaluate(
                "(el, html) => el.innerHTML = html", html
            )
            return True
    except Exception:
        pass

    return False


def _goto_new_post(page) -> bool:
    """
    依序嘗試多個「新增文章」網址，能進到任何一個就算成功。
    """
    for u in CANDIDATE_NEW_POST_URLS:
        try:
            page.goto(u, timeout=30000, wait_until="domcontentloaded")
            # 有標題欄位就代表頁面載入正確
            page.wait_for_selector(SEL_TITLE_INPUT, timeout=15000)
            return True
        except Exception:
            continue
    return False


def _hunt_post_url(page) -> str:
    """
    取得發佈後的文章網址：
    1) 先直接看當前網址是否 /post/123456
    2) 再掃描頁面上所有 <a> 連到 /post/... 的連結（避免回列表頁）
    """
    final_url = None

    # 1) 直接取當前網址
    for _ in range(30):  # 最多等 30 秒
        cur = page.url
        if re.search(r"/post/\d+", cur):
            final_url = cur
            break
        time.sleep(1)

    # 2) 從頁面連結補抓
    if not final_url:
        try:
            links = page.locator('a[href*="/post/"]').all()
            for a in links:
                href = a.get_attribute("href") or ""
                if re.search(r"/post/\d+", href):
                    final_url = href
                    break
        except Exception:
            pass

    return final_url or ""


def _login(page, email: str, password: str) -> None:
    """
    進入登入頁並完成登入（若已登入，PIXNET 通常會自動導到面板）。
    """
    page.goto(LOGIN_URL, timeout=30000, wait_until="domcontentloaded")
    try:
        # 有些情況已經登入；若看不到登入欄位就直接返回
        if page.locator(SEL_LOGIN_EMAIL).count() == 0:
            return
        page.fill(SEL_LOGIN_EMAIL, email)
        page.fill(SEL_LOGIN_PWD, password)
        page.click(SEL_LOGIN_SUBMIT)
        page.wait_for_load_state("networkidle", timeout=60000)
    except PWTimeout:
        # 就算逾時，有時也已完成登入，後續再試能不能進新文章頁
        pass


def pixnet_login_and_post(email: str, password: str,
                          title: str, content: str, tags: List[str]) -> Tuple[bool, str]:
    """
    主流程：登入 → 進新文章 → 填標題/內容/標籤 → 發佈 → 回傳文章網址
    回傳：
      (True, url)  成功
      (False, err) 失敗與錯誤訊息
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context()
            page = context.new_page()

            # 1) 登入
            _login(page, email, password)

            # 2) 進到新增文章頁
            if not _goto_new_post(page):
                return False, "無法開啟新增文章頁（可能未登入或面板網址改版）"

            # 3) 填標題
            page.fill(SEL_TITLE_INPUT, title)

            # 4) 填內容（CKEditor）
            if not _fill_ckeditor_frame(page, content):
                return False, "找不到 CKEditor 可編輯區，或填寫內容失敗"

            # 5) 填標籤（可留空；你有 selector 就填）
            try:
                if tags and page.locator(SEL_TAG_INPUT).count() > 0:
                    page.fill(SEL_TAG_INPUT, ", ".join(tags))
            except Exception:
                # 標籤失敗不致命，略過
                pass

            # 6) 發佈
            page.click(SEL_PUBLISH_BTN)

            # 7) 等待跳轉到文章頁 & 取文章網址
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeout:
                pass

            final_url = _hunt_post_url(page)

            context.close()
            browser.close()

            if not final_url:
                # 若沒拿到連結，回傳一個通用提示（方便你在 log 裡搜尋）
                return False, "已點擊發佈，但無法判定文章網址（可能仍在草稿或回列表頁）"

            return True, final_url

    except Exception as e:
        return False, f"例外：{e}"
