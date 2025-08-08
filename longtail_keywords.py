def generate_keywords_with_links():
    keywords = ["理債一日便優缺點分析", "2025年債務協商最新方法", "快速整合負債流程解析"]
    base_url = "https://lihi.cc/japMO"
    return [f"<a href='{base_url}'>{kw}</a>" for kw in keywords]
