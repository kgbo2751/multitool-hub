import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

def search_top_results(keyword: str, limit: int = 3):
    try:
        encoded_query = urllib.parse.quote_plus(keyword)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        response = requests.post(
            search_url,
            headers=HEADERS,
            data={"q": keyword},
            timeout=10,
        )

        if response.status_code != 200:
            return None, "검색 서버 응답 오류가 발생했습니다."

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        seen_urls = set()

        for a in soup.select("a.result__a"):
            raw_url = a.get("href", "")

            if "uddg=" in raw_url:
                target_url = urllib.parse.unquote(
                    raw_url.split("uddg=")[1].split("&")[0]
                )
            else:
                target_url = raw_url

            title = a.get_text(strip=True)

            if (
                target_url.startswith("http")
                and title
                and target_url not in seen_urls
            ):
                seen_urls.add(target_url)
                results.append({"title": title, "url": target_url})

                if len(results) >= limit:
                    break

        if not results:
            return None, "검색 결과를 찾을 수 없습니다."

        return results, None

    except Exception as e:
        return None, f"검색 중 오류 발생: {str(e)}"

def scrape_page_content(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(
            ["script", "style", "nav", "header", "footer", "aside", "noscript"]
        ):
            tag.extract()

        paragraphs = soup.find_all("p")
        text_lines = [
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        ]

        if not text_lines:
            text_lines = [
                line.strip()
                for line in soup.get_text().splitlines()
                if line.strip()
            ]

        full_text = "\n\n".join(text_lines)
        if not full_text:
            return "본문 텍스트를 파싱할 수 없는 페이지입니다 (동적 자바스크립트/이미지 전용)."

        return (
            (full_text[:1000] + "\n\n... (이하 생략)")
            if len(full_text) > 1000
            else full_text
        )

    except Exception as e:
        return f"본문 로딩 실패: {str(e)}"

def perform_search_and_scrape(keyword: str, limit: int = 3):
    top_links, err = search_top_results(keyword, limit=limit)
    if err:
        return {"success": False, "error": err}

    crawled_data = []
    for item in top_links:
        body = scrape_page_content(item["url"])
        crawled_data.append({
            "title": item["title"],
            "url": item["url"],
            "body": body
        })

    return {"success": True, "results": crawled_data}