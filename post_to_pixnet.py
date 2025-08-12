# 7) 等跳轉到文章頁，抓出文章網址
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

# 若沒抓到，保底從頁面所有 <a> 裡找含 /post/ 的連結
if not final_url:
    links = page.locator("a[href*='/post/']").all()
    for a in links:
        try:
            href = a.get_attribute("href")
            if href and "/post/" in href:
                final_url = href
                break
        except Exception:
            pass

# 收尾與回傳
context.close()
browser.close()

if final_url:
    return True, final_url
else:
    return False, "發表後未取得文章網址"
