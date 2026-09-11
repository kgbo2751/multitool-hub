import requests

API_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "도쿄": {"lat": 35.6762, "lon": 139.6503},
    "뉴욕": {"lat": 40.7128, "lon": -74.0060},
    "런던": {"lat": 51.5074, "lon": -0.1278}
}

WEATHER_DESC = {
    0: ("☀️ 맑음", "#FFA500"),
    1: ("🌤️ 대체로 맑음", "#FFD700"),
    2: ("⛅ 부분 구름", "#87CEEB"),
    3: ("☁️ 흐림", "#A9A9A9"),
    45: ("🌫️ 안개", "#D3D3D3"),
    48: ("🌫️ 빙결 안개", "#D3D3D3"),
    51: ("🌦️ 약한 이슬비", "#4682B4"),
    61: ("🌧️ 약한 비", "#1E90FF"),
    63: ("🌧️ 보통 비", "#1E90FF"),
    65: ("🌧️ 강한 비", "#0000CD"),
    71: ("🌨️ 약한 눈", "#E0FFFF"),
    73: ("🌨️ 보통 눈", "#E0FFFF"),
    75: ("❄️ 강한 눈", "#B0E0E6"),
    95: ("⛈️ 뇌우", "#483D8B")
}

def fetch_weather_forecast(city_name: str = "서울"):
    coord = CITIES.get(city_name, CITIES["서울"])
    params = {
        "latitude": coord["lat"],
        "longitude": coord["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "auto"
    }

    try:
        response = requests.get(API_URL, params=params, timeout=7)
        if response.status_code != 200:
            return []

        data = response.json()
        daily = data.get("daily", {})
        times = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weathercode", [])

        weather_list = []
        for i in range(len(times)):
            code = codes[i] if i < len(codes) else 0
            desc, color = WEATHER_DESC.get(code, ("🌦️ 날씨 정보", "#808080"))
            weather_list.append({
                "date": times[i],
                "temp_max": t_max[i] if i < len(t_max) else 0.0,
                "temp_min": t_min[i] if i < len(t_min) else 0.0,
                "precipitation": precip[i] if i < len(precip) else 0.0,
                "weather_desc": desc,
                "theme_color": color
            })
        return weather_list
    except Exception:
        return []