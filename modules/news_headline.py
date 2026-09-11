import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_top_headlines(country: str = "us"):
    if not NEWS_API_KEY:
        return []

    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url, timeout=7)
        data = response.json()
        if data.get("status") != "ok":
            return []
        
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", "No Title"),
                "image": a.get("urlToImage") or "",
                "url": a.get("url", "#")
            })
        return articles
    except Exception:
        return []