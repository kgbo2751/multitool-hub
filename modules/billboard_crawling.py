import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
}

def fetch_billboard_chart(url: str, limit: int = 100):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        chart_data = []
        seen = set()
        items = soup.select("li.o-chart-results-list__item")

        for item in items:
            title_tag = item.select_one("h3.c-title")
            artist_tag = item.select_one("span.c-label.a-no-trucate") or item.select_one("span.c-label")

            if title_tag and artist_tag:
                title = title_tag.get_text(strip=True)
                artist = artist_tag.get_text(strip=True)
                
                key = (title, artist)
                if key in seen:
                    continue
                seen.add(key)
                
                chart_data.append({"title": title, "artist": artist})

            if len(chart_data) >= limit:
                break

        return chart_data
    except Exception as e:
        print(f"[Error] Billboard Scraping Failed: {e}")
        return []