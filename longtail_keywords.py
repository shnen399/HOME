import random

def generate_keywords_with_links(n=3):
    all_keywords = [
        "2025年債務協商實用對策", "快速整合負債指南", "理債一日便真實經驗",
        "負債族如何翻身", "小白學理財", "信用卡負債處理流程"
    ]
    base_url = "https://lihi.cc/japMO"
    selected = random.sample(all_keywords, k=n)
    return [f'<a href="{base_url}">{kw}</a>' for kw in selected]
