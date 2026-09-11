import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VT_API_URL = "https://www.virustotal.com/api/v3/urls/"

def encode_url(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")

def scan_url(target_url: str):
    if not VIRUSTOTAL_API_KEY:
        return {"success": False, "error": "API 키가 설정되지 않았습니다."}

    encoded = encode_url(target_url)
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        response = requests.get(VT_API_URL + encoded, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            return {
                "success": True,
                "stats": {
                    "harmless": stats.get("harmless", 0),
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "undetected": stats.get("undetected", 0)
                }
            }
        elif response.status_code == 404:
            return {"success": False, "error": "VirusTotal 데이터베이스에 등록되지 않은 URL입니다."}
        else:
            return {"success": False, "error": f"검사 실패 (상태 코드: {response.status_code})"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}