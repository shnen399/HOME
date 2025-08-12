# post_to_pixnet.py

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import re, time

LOGIN_URL = "https://user.pixnet.net/login?service=blog"

# 你先前提供的 selector
SEL_LOGIN_EMAIL = "#signin__form--post > div.signin__section.signin__section-email > input"
SEL_LOGIN_PWD   = "input[name='password']"
SEL_LOGIN_SUBMIT = "#signin__form--post > button"

# 發文頁面（面板）
CANDIDATE_NEW_POST_URLS = [
    "https://panel.pixnet.cc/blog/articles/new",
    "https://panel.pixnet.net/blog/articles/new",
    "https://panel.pixnet.cc/blog/article/new",
    "https://panel.pixnet.net/blog/article/new",
]

SEL_TITLE_INPUT   = "#editArticle-header-title"
SEL_PUBLISH_BTN   = "#edit-article-footer > div.action-buttons > button.radius.text-primary.display-at-desktop"

def _fill_ckeditor_frame(page, html):
    # 找 CKEditor 的 iframe，對裡面的 body[contenteditable=true] 填內容
    frame = None
    for f in page.frames:
        try:
            if f.locator("body[contenteditable='true']").count():
                frame = f
                break
        except Exception:
            pass
    if not frame:
        # 保底再掃一次
        frames = page.locator("iframe").all()
        for fr in frames:
            try:
                f = fr.content_frame()
                if f and f.locator("body[contenteditable='true']").count():
                    frame = f
                    break
            except Exception:
                pass
    if not frame:
        raise RuntimeError("找不到 CKEditor 編輯器 iframe")

    body = frame.locator("body[contenteditable='true']")
    body.click()
    # 先清空（保守作法：全選 + 刪除）
    body.press("Control+A")
    body.press("Delete")
    # 直接注入 HTML（比打字快、也能保留段落）
    frame.evaluate(
        """(html) => { document.activeElement.innerHTML = html; }""",
        html
    )

def pixnet_login_and_post(user, pwd, title, content, tags):
    """
    真實登入 + 發文
    回傳：(True, 文章網址) 或 (False, 錯誤訊息)
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = browser.new_context()
            page = ctx.new_page()

            # 1) 登入
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            page.fill(SEL_LOGIN_EMAIL, user)
            page.fill(SEL_LOGIN_PWD, pwd)
            page.click(SEL_LOGIN_SUBMIT)

            # 等登入完成：看是否跳轉到 panel 相關網域或顯示使用者 UI
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeout:
                pass

            # 2) 進到發文頁（不同帳號介面可能不一，這裡嘗試多個候選 URL）
            opened = False
            for u in CANDIDATE_NEW_POST_URLS:
                try:
                    page.goto(u, wait_until="domcontentloaded", timeout=45000)
                    # 標題欄位與 CKEditor 都要能找到才算成功進入編輯頁
                    if page.locator(SEL_TITLE_INPUT).count():
                        opened = True
                        break
                except Exception:
                    continue

            if not opened:
                raise RuntimeError("進入『新增文章』頁面失敗，請確認發文頁 URL 或權限。")

            # 3) 填標題
            page.fill(SEL_TITLE_INPUT, title)

            # 4) 填內容（CKEditor iframe）
            _fill_ckeditor_frame(page, content)

           # 5) 填標籤
page.fill("#editArticle-header-tag-input", ", ".join(tags))
            # 6) 發表
            page.click(SEL_PUBLISH_BTN)

            # 7) 等待跳轉到文章頁，抓出文章網址
            final_url = None
            try:
                page.wait_for_load_state("networkidle", timeout=60000)
            except PWTimeout:
                pass

            # 文章頁通常包含 /post/（若不同可調整判斷）
            for _ in range(30):
                cur = page.url
                if re.search(r"/post/\d+", cur):
                    final_url = cur
                    break
                time.sleep(1)

            if not final_url:
                # 有些會發表後跳回列表，再從提示或按鈕取連結；這裡保底抓 <a> 連結
                links = page.locator("a[href*='/post/']").all()
                for a in links:
                    try:
                        href = a.get_attribute("href")
                        if href and "/post/" in href:
                            final_url = href
                            break
                    except Exception:
                        pass

            if not final_url:
                raise RuntimeError("已點發表，但無法取得文章網址（可能介面變動，需更新 selector）")

            browser.close()
            return True, final_url

    except Exception as e:
        try:
            browser.close()
        except Exception:
            pass
        return False, f"發文失敗：{e}"
