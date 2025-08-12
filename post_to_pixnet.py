# post_to_pixnet.py
# 規格：pixnet_login_and_post(email, password, title, content, tags) -> (bool, str)

from typing import List, Tuple, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import re, time

LOGIN_URL = "https://user.pixnet.net/login?service=blog"

# 發文頁（面板）可能有不同網域/路徑，這裡列出幾個候選網址逐一嘗試
CANDIDATE_NEW_POST_URLS = [
    "https://panel.pixnet.cc/blog/articles/new",
    "https://panel.pixnet.net/blog/articles/new",
    "https://panel.pixnet.net/blog/article/new",
    "https://panel.pixnet.cc/blog/article/new",
]

# Login 頁面 selector（盡量使用穩定屬性）
SEL_LOGIN_EMAIL  = "input[name='email']"
SEL_LOGIN_PWD    = "input[name='password']"
SEL_LOGIN_SUBMIT = "button[type='submit']"

# 發文頁面 selector
SEL_TITLE_INPUT  = "#editArticle-header-title, input#editArticle-header-title"
SEL_TAG_INPUT    = "#editArticle-header-tag-input"  # 你之前加的標籤欄位
SEL_PUBLISH_BTN  = "#edit-article-footer .action-buttons button[type='submit'], #edit-article-footer .action-buttons button"

def _wait_for_any(page, selectors: str, timeout: int = 15000) -> Optional[str]:
    """
    等待任一 selector 出現；selectors 用逗號分隔的 CSS 群組選擇器即可。
    回傳實際可用的 selector（第一個真的存在的）
    """
    # Playwright 的 .locator(...).first 可以配群組，但為了保守我們逐一試
    for sel in [s.strip() for s in selectors.split(",")]:
        if not sel:
            continue
        try:
            page.wait_for_selector(sel, timeout=timeout, state="visible")
            return sel
        except PWTimeout:
            continue
    return None

def _fill_ckeditor_frame(page, html: str) -> bool:
    """
    嘗試尋找 CKEditor 的 contenteditable 區塊，直接寫入 innerHTML。
    有些時候在主頁面、有時在 iframe，所以兩邊都試。
    """
    # 1) 先試主頁面
    try:
        el = page.locator('body[contenteditable="true"], [contenteditable="true"]').first
        if el and el.count() > 0:
            el.evaluate("(node, html) => node.innerHTML = html", html)
            return True
    except Exception:
        pass

    # 2) 再試每個 frame
    try:
        for fr in page.frames:
            try:
                fr.wait_for_selector('[contenteditable="true"]', timeout=3000)
                el = fr.locator('[contenteditable="true"]').first
                if el and el.count() > 0:
                    el.evaluate("(node, html) => node.innerHTML = html", html)
                    return True
            except Exception:
                continue
    except Exception:
        pass

    return False

def _safe_click(page, selector: str, timeout: int = 15000) -> bool:
    try:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        page.click(selector, timeout=timeout)
        return True
    except Exception:
        return False

def _try_extract_post_url(page) -> Optional[str]:
    """
    盡量把發表後的文章網址找出來：
    1) 直接用目前 URL（多半包含 /post/123456）
    2) 退而求其次：頁面上所有 a[href*='/post/'] 的連結
    """
    try:
        cur = page.url or ""
        if re.search(r"/post/\d+", cur):
            return cur
    except Exception:
        pass

    # Fallback：掃描 <a>
    try:
        links = page.locator("a[href*='/post/']").all()
        for a in links:
            try:
                href = a.get_attribute("href") or ""
                if "/post/" in href:
                    return href
            except Exception:
                continue
    except Exception:
        pass
    return None

def pixnet_login_and_post(email: str, password: str, title: str, content: str, tags: List[str]) -> Tuple[bool, str]:
    """
    登入 PIXNET，打開新文章頁，填標題/內文/標籤，然後發表。
    成功回傳 (True, 文章網址)；失敗回傳 (False, 錯誤訊息)。
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ],
            )
            context = browser.new_context()
            page = context.new_page()

            # 1) Login
            page.goto(LOGIN_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_selector(SEL_LOGIN_EMAIL, timeout=30000)
            page.fill(SEL_LOGIN_EMAIL, email)
            page.fill(SEL_LOGIN_PWD, password)
            page.click(SEL_LOGIN_SUBMIT)
            # 等待導回面板/首頁（登入成功通常會跳轉）
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except PWTimeout:
                pass

            # 2) 打開新文章頁（多個候選網址逐一嘗試）
            opened = False
            for url in CANDIDATE_NEW_POST_URLS:
                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    # 等標題欄出現
                    ok_sel = _wait_for_any(page, SEL_TITLE_INPUT, timeout=15000)
                    if ok_sel:
                        opened = True
                        break
                except Exception:
                    continue

            if not opened:
                context.close(); browser.close()
                return False, "打不開發文頁（title 欄位找不到）"

            # 3) 填標題
            title_sel = _wait_for_any(page, SEL_TITLE_INPUT, timeout=15000)
            if not title_sel:
                context.close(); browser.close()
                return False, "找不到標題欄位"
            page.fill(title_sel, title)

            # 4) 填內容（CKEditor）
            filled = _fill_ckeditor_frame(page, content)
            if not filled:
                # 如果沒成功就再等一下 DOM
                time.sleep(1.5)
                filled = _fill_ckeditor_frame(page, content)
            if not filled:
                context.close(); browser.close()
                return False, "找不到 CKEditor 內容區塊（contenteditable）"

            # 5)（選）填標籤
            try:
                if tags:
                    if _wait_for_any(page, SEL_TAG_INPUT, timeout=3000):
                        page.fill(SEL_TAG_INPUT, ", ".join(tags[:10]))  # 最多塞 10 個以免過長
            except Exception:
                pass  # 標籤不是硬性需求，失敗不擋流程

            # 6) 發表
            if not _safe_click(page, SEL_PUBLISH_BTN, timeout=20000):
                context.close(); browser.close()
                return False, "找不到『發表』按鈕或無法點擊"

            # 7) 等跳轉並抓文章網址
            final_url = None
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeout:
                pass

            # 先直接看目前網址
            final_url = _try_extract_post_url(page)

            # 若還沒有，給它一些時間輪詢
            if not final_url:
                for _ in range(20):
                    time.sleep(1)
                    final_url = _try_extract_post_url(page)
                    if final_url:
                        break

            # 8) 收尾與回傳
            context.close()
            browser.close()

            if final_url:
                return True, final_url
            else:
                return False, "發文後找不到文章網址"

    except Exception as e:
        # 任意例外
        try:
            context.close()
            browser.close()
        except Exception:
            pass
        return False, f"例外錯誤：{e}"
