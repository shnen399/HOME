# Render 部署小包（Playwright 版）

把以下三個檔案放在專案根目錄：
- requirements.txt
- render-build.sh
- startup.sh

Render 設定：
- Build Command: bash render-build.sh
- Start Command: bash startup.sh

部署前：在 Render 後台點「Manual Deploy → Clear build cache」，再 Deploy latest commit。

如果還遇到 Chromium 缺失，startup.sh 會在啟動時自動補裝一次。
