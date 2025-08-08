def is_valid_news_url(url):
    invalid_patterns = [
        "cloudflare.com", "5xx", "error", "404", "expired", "login", "ads"
    ]
    return not any(p in url for p in invalid_patterns)


# 範例：在實際抓新聞時使用
def filter_valid_news_urls(urls):
    return [url for url in urls if is_valid_news_url(url)]
