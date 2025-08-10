# PIXNET AutoPoster（多帳號 + 新聞 + 2000字 + 長尾關鍵字固定連結 + 完整紀錄）

## 部署步驟（Render）
1) 將本專案上傳到 GitHub 或直接在 Render 建立 Web Service。
2) Build Command：`pip install -r requirements.txt`
3) Start Command：`uvicorn main:app --host 0.0.0.0 --port 10000`
4) 在根目錄編輯 `xmynvilbkqgkknlide@nespf.com:co13572888`（每行：`email:password`）。
5) （選）Render → Environment 變數可設定：
   - `FIXED_LINK`：長尾關鍵字要導向的固定連結（預設 https://lihi.cc/japMO）
   - `PIXNET_ACCOUNTS_FILE`：帳密檔檔名（預設 pixnet_accounts.txt）
   - `LINE_NOTIFY_TOKEN`：若填入，發文成功/失敗會通知到你的 LINE Notify
6) 部署後開 `https://你的服務/docs` → `POST /post_article` 立即測試；
   排程會每 3 分鐘自動抓新聞→生成 2000+ 字→多帳號輪流發文。

## 發文紀錄
- 所有成功/失敗都會寫入 `發文紀錄.txt`（JSON Lines），包含：
  - 帳號、狀態（success/fail）、文章標題、文章連結（成功時）、錯誤訊息（失敗時）
  - 使用的新聞（來源、標題、連結、封面圖）

## 注意
- `post_to_pixnet.py` 內提供了 `pixnet_login_and_post()` 的**佔位實作**，請替換為你現有的登入+發文邏輯（Selenium 或 requests）。
  - 介面：`pixnet_login_and_post(user, pwd, title, content, tags) -> (bool, str)`
  - 成功：`(True, 文章網址)`；失敗：`(False, "錯誤訊息")`
- 多帳號：同一帳號連續失敗達 3 次會被加入 `bad_accounts.txt`（不會自動刪檔，方便你檢查）。
