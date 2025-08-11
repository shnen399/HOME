# Web & API
fastapi>=0.110,<0.114
uvicorn>=0.29,<0.32

# Scheduler
apscheduler>=3.10,<3.11

# HTTP & 解析
requests>=2.31,<3.0
beautifulsoup4>=4.12,<5.0
lxml>=5.2,<6.0

# 為了相依（例如有些套件需要），允許使用 3.1.x 的預編譯 wheel，避免編譯失敗
greenlet>=3.1,<3.3
然後在 Render 的 Build Command 用這一行（請貼在 Settings → Build & Deploy → Build Command）：

lua
複製
編輯
pip install --upgrade pip setuptools wheel && pip install "greenlet>=3.1,<3.3" --only-binary=:all: && pip install -r requirements.txt
Start Command 請維持（或改成）：

nginx
複製
編輯
uvicorn main:app --host 0.0.0.0 --port $PORT
