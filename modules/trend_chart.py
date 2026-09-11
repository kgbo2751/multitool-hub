import feedparser

def fetch_google_trends(geo: str = "KR", limit: int = 15):
    rss_url = f"https://trends.google.co.kr/trending/rss?geo={geo}"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return []
    
    trend_list = []
    for entry in feed.entries[:limit]:
        trend_list.append({
            "title": entry.title,
            "traffic": getattr(entry, "ht_approx_traffic", "N/A"),
            "link": entry.link
        })
        
    return trend_list