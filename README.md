# PIXNET AutoPoster — Playwright 版（Render 免下載部署）

## 特色
- FastAPI `/docs`、`/post_article`
- Playwright 自動登入發文（較 Selenium 穩定）
- APScheduler 每 3 分鐘自動發文（24/7）
- 熱門新聞抓取 + 2000+字文案 + 長尾關鍵字（導向 FIXED_LINK）
- 多帳號輪播、失敗 3 次自動刪除、LINE Notify

## 佈署
1. 推到 GitHub → Render 建立 Web Service（Docker）或 Blueprint（render.yaml）。
2. 設環境變數：
   - `PIXNET_ACCOUNTS`（多行：`email:password:blog_url`）
   - `FIXED_LINK`（例：`https://lihi.cc/japMO`）
   - `LINE_NOTIFY_TOKEN`（選填）
3. Deploy 完成 → 打開 `/docs` 測 `POST /post_article`。

## 結構
```
.
├─ render.yaml
├─ Dockerfile
├─ requirements.txt
└─ app/
   ├─ main.py
   ├─ scheduler.py
   ├─ panel_article.py
   ├─ news_fetcher.py
   ├─ article_generator.py
   ├─ utils.py
   └─ selectors.json
```
