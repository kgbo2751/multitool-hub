import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
FALLBACK_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

def fetch_movies(category: str):
    if not TMDB_API_KEY:
        return []

    if category == "trending":
        url = f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}"
    else:
        url = f"{BASE_URL}/movie/{category}?api_key={TMDB_API_KEY}&language=en-US&page=1"

    try:
        response = requests.get(url, timeout=7)
        response.raise_for_status()
        data = response.json()
        
        movies = []
        for item in data.get("results", []):
            poster_path = item.get("poster_path")
            movies.append({
                "title": item.get("title", "Unknown Title"),
                "poster": f"{POSTER_BASE_URL}{poster_path}" if poster_path else FALLBACK_POSTER,
                "release_date": item.get("release_date", "N/A"),
                "rating": item.get("vote_average", 0.0)
            })
        return movies
    except Exception:
        return []