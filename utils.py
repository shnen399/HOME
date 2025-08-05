
import os

def post_to_pixnet(article):
    accounts = os.getenv("PIXNET_ACCOUNTS", "")
    account_list = accounts.split(",")

    for acc in account_list:
        try:
            username, password = acc.split(":")
            print(f"正在使用帳號 {username} 發文...")
            print(f"標題: {article['title']}")
            print(f"內容: {article['content']}")
            print(f"標籤: {article['tags']}")
        except Exception as e:
            print(f"帳號 {acc} 發文失敗: {e}")
