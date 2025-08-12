# Dockerfile for Render (Playwright preinstalled)

將這個 Dockerfile 放在專案根目錄，Render 會自動偵測 Docker 並建置。
- 不需要再設定 Build/Start Command。
- 需要的條件：你的 FastAPI 進入點是 `main:app`（如果不同，調整最後一行的模組路徑）。

步驟：
1. 上傳 Dockerfile 至專案根目錄。
2. Render → Manual Deploy → Clear build cache & deploy。
3. 部署完成後，再測試 `/docs` 與 `/post_article`。
