import urllib.parse
import streamlit.components.v1 as components

MAP_LOCATIONS = {
    "서울 시청": "서울특별시 중구 세종대로 110",
    "강남역": "서울특별시 강남구 강남대로 396",
    "판교 테크노밸리": "경기도 성남시 분당구 판교역로",
    "부산 시청": "부산광역시 연제구 중앙대로 1001",
    "인천국제공항": "인천광역시 중구 공항로 272"
}

def render_google_map(query_location: str, height: int = 650):
    encoded = urllib.parse.quote(query_location)
    embed_url = f"https://maps.google.com/maps?q={encoded}&t=&z=15&ie=UTF8&iwloc=&output=embed"
    components.iframe(embed_url, height=height)