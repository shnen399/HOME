# PIXNET 自動發文（Ready-To-Run）

已內建真實帳號，解壓縮即可直接執行。

## 步驟
1. `pip install -r requirements.txt`
2. `uvicorn app:app --host 0.0.0.0 --port 8000`
3. 打開 `http://127.0.0.1:8000/ui` 按「立即發文」測試（同時每 180 秒自動發文）

## 參數
- 預設每 180 秒排程一次（環境變數 `INTERVAL_SECONDS` 可改）
- 連續失敗 ≥3 次自動刪帳號行
- 成功發文抓文章連結記錄到 `發文紀錄.txt` 與 `data.db`

若之後要新增帳號，直接編輯根目錄的 `pixnet_accounts.txt`，每行 `email:password`。
