import streamlit as st
from dotenv import load_dotenv
from streamlit_drawable_canvas import st_canvas

load_dotenv()

from modules.movie_chart import fetch_movies
from modules.billboard_crawling import fetch_billboard_chart
from modules.news_headline import fetch_top_headlines
from modules.finance_chart import get_stock_data
from modules.trend_chart import fetch_google_trends
from modules.weather_chart import fetch_weather_forecast, CITIES
from modules.url_security_search import scan_url
from modules.pc_security_search import capture_packets, search_shodan_ip
from modules.paint import save_drawing_image
from modules.image_ocr import extract_text_from_bytes
from modules.image_color_extract import extract_dominant_colors
from modules.audio_stt import transcribe_audio_file
from modules.speech_recognition import recognize_speech_from_audio
from modules.tts_service import generate_speech
from modules.live_chat import get_room_messages, send_room_message
from modules.web_crawling import perform_search_and_scrape
from modules.web_macro import run_google_image_macro
from modules.google_map import render_google_map, MAP_LOCATIONS
from modules.huggingface_chatbot import get_hf_response
from modules.db_memo import render_todo_ui
from modules.db_stock import render_stock_game

st.set_page_config(
    page_title="Multitool Hub",
    page_icon="🛠️",
    layout="wide"
)

@st.cache_data(ttl=3600)
def cached_movies(category: str):
    return fetch_movies(category)

@st.cache_data(ttl=7200)
def cached_billboard(url: str, limit: int = 100):
    return fetch_billboard_chart(url, limit)

@st.cache_data(ttl=1800)
def cached_news(country: str = "us"):
    return fetch_top_headlines(country)

@st.cache_data(ttl=600)
def cached_stocks():
    return get_stock_data()

@st.cache_data(ttl=1800)
def cached_trends(geo: str = "KR"):
    return fetch_google_trends(geo)

@st.cache_data(ttl=1800)
def cached_weather(city: str = "서울"):
    return fetch_weather_forecast(city)

def render_movies():
    st.title("🎬 Movie Box Office Charts")
    st.caption("The Movie Database (TMDB) API 연동")

    category_map = {
        "Popular (현재 인기)": "popular",
        "Top Rated (평점 순)": "top_rated",
        "Now Playing (상영 중)": "now_playing",
        "Upcoming (출시 예정)": "upcoming",
        "Trending (요즘 인기)": "trending"
    }

    tabs = st.tabs(list(category_map.keys()))

    for tab, (label, cat_key) in zip(tabs, category_map.items()):
        with tab:
            with st.spinner("영화 데이터를 불러오는 중입니다..."):
                movie_list = cached_movies(cat_key)

            if not movie_list:
                st.warning("데이터를 불러오지 못했습니다. (.env API 키 설정을 확인하세요)")
                continue

            cols_per_row = 4
            for i in range(0, len(movie_list), cols_per_row):
                row_items = movie_list[i:i + cols_per_row]
                cols = st.columns(cols_per_row)
                for col, movie in zip(cols, row_items):
                    with col:
                        with st.container(border=True):
                            st.image(movie["poster"], use_container_width=True)
                            st.markdown(f"**{movie['title']}**")
                            st.caption(f"📅 개봉: {movie['release_date']}")
                            st.markdown(f"⭐ **{movie['rating']:.1f}** / 10.0")

def render_billboard():
    st.title("🎵 Billboard Music Charts")
    st.caption("Billboard.com 실시간 크롤링")

    charts = [
        {"title": "Hot 100", "url": "https://www.billboard.com/charts/hot-100", "header_bg": "#d4edda"},
        {"title": "Billboard 200", "url": "https://www.billboard.com/charts/billboard-200", "header_bg": "#ffeeba"},
        {"title": "Global 200", "url": "https://www.billboard.com/charts/billboard-global-200", "header_bg": "#d1ecf1"},
        {"title": "Artist 100", "url": "https://www.billboard.com/charts/artist-100", "header_bg": "#e2d9f3"}
    ]

    cols = st.columns(4)

    for idx, cfg in enumerate(charts):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="background-color: {cfg['header_bg']}; padding: 8px; border-radius: 6px; 
                            text-align: center; font-weight: bold; color: #222; margin-bottom: 8px;">
                    {cfg['title']}
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.spinner(f"{cfg['title']} 파싱 중..."):
                entries = cached_billboard(cfg["url"], limit=100)

            with st.container(height=700):
                if not entries:
                    st.caption("차트 데이터를 가져올 수 없습니다.")
                else:
                    for rank, song in enumerate(entries, start=1):
                        if cfg["title"] == "Artist 100":
                            st.markdown(f"**{rank}.** {song['artist']}")
                        else:
                            st.markdown(
                                f"**{rank}.** {song['title']}<br>"
                                f"<span style='color: #666; font-size: 0.85em;'>{song['artist']}</span>",
                                unsafe_allow_html=True
                            )
                        st.divider()

def render_news():
    st.title("📰 Top News Headlines")
    st.caption("NewsAPI 실시간 주요 헤드라인")

    country_options = {"미국 (US)": "us", "한국 (KR)": "kr", "일본 (JP)": "jp", "영국 (GB)": "gb"}
    selected_country_label = st.selectbox("국가 선택", list(country_options.keys()))
    country_code = country_options[selected_country_label]

    with st.spinner("최신 뉴스를 가져오는 중입니다..."):
        articles = cached_news(country_code)

    if not articles:
        st.warning("뉴스를 불러오지 못했습니다. (.env API 키 설정을 확인하세요)")
        return

    cols_per_row = 3
    for i in range(0, len(articles), cols_per_row):
        row_items = articles[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, article in zip(cols, row_items):
            with col:
                with st.container(border=True):
                    if article["image"]:
                        st.image(article["image"], use_container_width=True)
                    st.markdown(f"**[{article['title']}]({article['url']})**")

def render_stocks():
    st.title("📈 주요 종목 주가 시세")
    st.caption("Yahoo Finance (yfinance) 실시간 데이터 연동")

    with st.spinner("주가 데이터를 집계 중입니다..."):
        stock_list = cached_stocks()

    if not stock_list:
        st.warning("주가 정보를 불러오지 못했습니다.")
        return

    cols = st.columns(len(stock_list))
    for col, stock in zip(cols, stock_list):
        with col:
            with st.container(border=True):
                currency = "KRW" if ".KS" in stock["ticker"] else "USD"
                st.metric(
                    label=f"{stock['name']} ({stock['ticker']})",
                    value=f"{stock['price']} {currency}",
                    delta=stock["delta"]
                )

def render_trends():
    st.title("🔥 실시간 급상승 트렌드")
    st.caption("Google Trends 실시간 인기 검색어 RSS 연동")

    country_map = {"대한민국": "KR", "미국": "US", "일본": "JP", "영국": "GB"}
    selected_country = st.selectbox("지역 선택", list(country_map.keys()))
    geo_code = country_map[selected_country]

    with st.spinner("트렌드 데이터를 가져오는 중입니다..."):
        trends = cached_trends(geo_code)

    if not trends:
        st.warning("트렌드 데이터를 불러오지 못했습니다.")
        return

    for idx, item in enumerate(trends, start=1):
        with st.container(border=True):
            col_rank, col_content, col_traffic = st.columns([1, 7, 2])
            with col_rank:
                st.markdown(f"### #{idx}")
            with col_content:
                st.markdown(f"**[{item['title']}]({item['link']})**")
            with col_traffic:
                st.caption("검색량")
                st.markdown(f"`{item['traffic']}`")

def render_weather():
    st.title("🌤️ 주간 날씨 예보")
    st.caption("Open-Meteo API 기상 예보 데이터 연동")

    city = st.selectbox("도시 선택", list(CITIES.keys()))

    with st.spinner("일기예보를 가져오는 중입니다..."):
        forecasts = cached_weather(city)

    if not forecasts:
        st.warning("날씨 정보를 불러오지 못했습니다.")
        return

    cols = st.columns(len(forecasts))
    for col, day in zip(cols, forecasts):
        with col:
            with st.container(border=True):
                st.markdown(f"**{day['date']}**")
                st.markdown(f"### {day['weather_desc']}")
                st.markdown(f"🔺 최고: **{day['temp_max']}°C**")
                st.markdown(f"🔻 최저: **{day['temp_min']}°C**")
                st.caption(f"💧 강수: {day['precipitation']}mm")

def render_security():
    st.title("🛡️ URL 악성 여부 검사기")
    st.caption("VirusTotal API v3 연동 보안 스캐너")

    target_url = st.text_input("검사할 URL 입력 (예: https://example.com)", placeholder="https://")

    if st.button("안전성 검사 시작", use_container_width=True):
        if not target_url:
            st.warning("URL을 입력해주세요.")
            return

        with st.spinner("보안 엔진 검사 중..."):
            result = scan_url(target_url)

        if not result.get("success"):
            st.error(result.get("error"))
        else:
            stats = result["stats"]
            malicious_count = stats["malicious"]
            suspicious_count = stats["suspicious"]

            if malicious_count > 0:
                st.error(f"⚠️ 위험: {malicious_count}개의 백신 엔진이 악성 코드로 감지했습니다.")
            elif suspicious_count > 0:
                st.warning(f"⚡ 주의: {suspicious_count}개의 백신 엔진이 의심 사이트로 분류했습니다.")
            else:
                st.success("✅ 안전: 악성 코드가 감지되지 않은 URL입니다.")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="안전 (Harmless)", value=stats["harmless"])
            with col2:
                st.metric(label="악성 (Malicious)", value=stats["malicious"])
            with col3:
                st.metric(label="의심 (Suspicious)", value=stats["suspicious"])
            with col4:
                st.metric(label="미탐지 (Undetected)", value=stats["undetected"])

def render_pc_security():
    st.title("🖥️ PC 네트워크 보안 및 OSINT")
    st.caption("Scapy 패킷 스니핑 & Shodan IP 인텔리전스")

    tab1, tab2 = st.tabs(["🌐 Shodan IP 검색", "📡 로컬 TCP 패킷 캡처"])

    with tab1:
        st.subheader("공인 IP 호스트 정보 조회")
        target_ip = st.text_input("조회할 IP 주소 입력 (예: 8.8.8.8)", placeholder="IP 주소 입력")
        if st.button("IP 정보 조회", use_container_width=True):
            if not target_ip:
                st.warning("IP 주소를 입력해주세요.")
            else:
                with st.spinner("Shodan 인텔리전스 데이터 조회 중..."):
                    shodan_res = search_shodan_ip(target_ip)

                if not shodan_res.get("success"):
                    st.error(shodan_res.get("error"))
                else:
                    data = shodan_res["data"]
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**IP:** `{data['ip']}`")
                        st.markdown(f"**기관 (Org):** {data['org']}")
                        st.markdown(f"**ISP:** {data['isp']}")
                    with c2:
                        st.markdown(f"**국가:** {data['country']}")
                        st.markdown(f"**운영체제 (OS):** {data['os']}")

                    st.divider()
                    st.markdown(f"**개방 포트:** {', '.join(map(str, data['ports'])) if data['ports'] else 'None'}")
                    if data["vulns"]:
                        st.error(f"**발견된 CVE 취약점:** {', '.join(data['vulns'])}")

    with tab2:
        st.subheader("실시간 로컬 TCP 패킷 캡처 (Scapy)")
        pkt_count = st.slider("캡처할 패킷 수", min_value=5, max_value=50, value=10)
        if st.button("패킷 캡처 시작", use_container_width=True):
            with st.spinner("TCP 패킷을 수집하고 있습니다 (최대 5초 대기)..."):
                sniff_res = capture_packets(count=pkt_count)

            if not sniff_res.get("success"):
                st.error(f"패킷 캡처 실패: {sniff_res.get('error')}")
            else:
                packets = sniff_res.get("packets", [])
                if not packets:
                    st.info("수집된 TCP 패킷이 없습니다.")
                else:
                    st.dataframe(packets, use_container_width=True)

def render_paint():
    st.title("🎨 그림판")
    st.caption("HTML5 Canvas 그래픽스 도구")

    c1, c2, c3 = st.columns([2, 2, 6])
    with c1:
        stroke_color = st.color_picker("펜 색상 선택", "#000000")
    with c2:
        stroke_width = st.slider("펜 굵기", 1, 25, 3)

    canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=450,
        width=700,
        drawing_mode="freedraw",
        key="canvas"
    )

    if st.button("그림 파일로 저장 (Paint/drawing.png)", use_container_width=True):
        if canvas_result.image_data is not None:
            res = save_drawing_image(canvas_result.image_data)
            if res.get("success"):
                st.success(f"이미지가 성공적으로 저장되었습니다: {res['path']}")
            else:
                st.error(f"저장 실패: {res.get('error')}")
        else:
            st.warning("캔버스에 그림이 없습니다.")

def render_ocr():
    st.title("📷 이미지 OCR 문자 인식")
    st.caption("EasyOCR 딥러닝 기반 텍스트 추출 (한국어/영어)")

    uploaded_file = st.file_uploader(
        "이미지 파일을 업로드하세요", 
        type=["png", "jpg", "jpeg", "gif", "bmp"]
    )

    if uploaded_file is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("업로드된 이미지")
            st.image(uploaded_file, use_container_width=True)

        with c2:
            st.subheader("추출된 텍스트")
            if st.button("문자 추출 시작", use_container_width=True):
                with st.spinner("이미지에서 문자를 인식하고 있습니다..."):
                    file_bytes = uploaded_file.read()
                    res = extract_text_from_bytes(file_bytes)

                if not res.get("success"):
                    st.error(f"추출 실패: {res.get('error')}")
                else:
                    st.text_area("인식 결과", value=res.get("text"), height=300)

def render_color_extract():
    st.title("🎨 이미지 색상 추출")
    st.caption("Scikit-Learn K-Means 클러스터링 기반 지배 색상 분석")

    k_val = st.slider("추출할 색상 수 (K)", min_value=3, max_value=8, value=5)
    uploaded_file = st.file_uploader(
        "색상을 추출할 이미지 파일을 업로드하세요",
        type=["png", "jpg", "jpeg", "gif", "bmp", "webp"]
    )

    if uploaded_file is not None:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("업로드 이미지")
            st.image(uploaded_file, use_container_width=True)

        with c2:
            st.subheader("추출 결과")
            if st.button("대표 색상 분석 시작", use_container_width=True):
                with st.spinner("색상 클러스터링 연산 중..."):
                    file_bytes = uploaded_file.read()
                    res = extract_dominant_colors(file_bytes, k=k_val)

                if not res.get("success"):
                    st.error(f"추출 실패: {res.get('error')}")
                else:
                    for color in res.get("colors", []):
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <div style="width: 45px; height: 45px; background-color: {color['hex']}; 
                                            border-radius: 8px; border: 1px solid #ccc; margin-right: 12px;"></div>
                                <div>
                                    <span style="font-weight: bold; font-size: 1.05em;">{color['hex']}</span>
                                    <span style="color: #666; font-size: 0.9em; margin-left: 8px;">{color['rgb']}</span><br>
                                    <span style="color: #444; font-size: 0.85em;">점유율: <b>{color['percent']}%</b></span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

def render_audio_stt():
    st.title("🎙️ 음성 인식 (Whisper STT)")
    st.caption("OpenAI Whisper 딥러닝 기반 다국어 음성 텍스트 변환")

    uploaded_audio = st.file_uploader(
        "음성 파일을 업로드하세요",
        type=["mp3", "wav", "m4a", "ogg", "flac"]
    )

    if uploaded_audio is not None:
        st.audio(uploaded_audio)
        if st.button("음성 인식 시작", use_container_width=True):
            with st.spinner("음성을 텍스트로 변환 중입니다 (Whisper 로컬 추론)..."):
                res = transcribe_audio_file(uploaded_audio)

            if not res.get("success"):
                st.error(f"변환 실패: {res.get('error')}")
            else:
                st.success(f"감지된 언어 코드: `{res.get('language')}`")
                st.text_area("변환된 텍스트", value=res.get("text"), height=250)

def render_speech_recognition():
    st.title("🎙️ 음성 인식 (SpeechRecognition)")
    st.caption("Google Web Speech API & 브라우저 마이크 연동")

    lang_choice = st.selectbox("인식 언어 선택", ["한국어 (ko-KR)", "영어 (en-US)"])
    lang_code = "ko-KR" if "한국어" in lang_choice else "en-US"

    audio_record = st.audio_input("마이크로 음성을 녹음하세요")

    if audio_record is not None:
        if st.button("음성 인식 시작", use_container_width=True):
            with st.spinner("음성을 텍스트로 변환 중..."):
                res = recognize_speech_from_audio(audio_record, language=lang_code)

            if not res.get("success"):
                st.error(res.get("error"))
            else:
                st.success("음성 인식 완료")
                st.text_area("변환 결과", value=res.get("text"), height=150)

def render_tts():
    st.title("🔊 텍스트 음성 변환 (TTS)")
    st.caption("Google Translate TTS (gTTS) 음성 합성")

    lang_dict = {
        "한국어 (ko)": "ko",
        "영어 (en)": "en",
        "일본어 (ja)": "ja",
        "중국어 (zh-CN)": "zh-CN"
    }
    selected_lang_label = st.selectbox("언어 선택", list(lang_dict.keys()))
    lang_code = lang_dict[selected_lang_label]

    input_text = st.text_area("음성으로 변환할 텍스트를 입력하세요", height=150, placeholder="여기에 텍스트를 입력하세요...")

    if st.button("음성 변환 및 생성", use_container_width=True):
        if not input_text.strip():
            st.warning("변환할 텍스트를 입력해주세요.")
            return

        with st.spinner("음성을 합성하고 있습니다..."):
            res = generate_speech(input_text, lang=lang_code)

        if not res.get("success"):
            st.error(f"음성 생성 실패: {res.get('error')}")
        else:
            st.success(f"생성 완료: {res.get('file_path')}")
            st.audio(res["audio_bytes"], format="audio/mp3")
            st.download_button(
                label="MP3 음성 파일 다운로드",
                data=res["audio_bytes"],
                file_name="tts_output.mp3",
                mime="audio/mp3",
                use_container_width=True
            )

def render_live_chat():
    st.title("💬 실시간 오픈 라이브챗 (Live Chat)")
    st.caption("인메모리 브로드캐스트 기반 실시간 다중 사용자 채팅방")

    col_room, col_user, col_refresh = st.columns([3, 3, 2])
    with col_room:
        room_name = st.selectbox("채팅방 선택", ["Lounge", "Developers", "Media", "Random"])
    with col_user:
        nickname = st.text_input("닉네임 설정", value=st.session_state.get("chat_nick", "Guest"))
        st.session_state["chat_nick"] = nickname
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄 새 메시지 새로고침", use_container_width=True):
            st.rerun()

    messages = get_room_messages(room_name)

    with st.container(border=True, height=450):
        if not messages:
            st.caption("아직 대화 내용이 없습니다. 첫 메시지를 남겨보세요.")
        else:
            for msg in messages:
                is_me = (msg["sender"] == nickname)
                role = "user" if is_me else "assistant"
                with st.chat_message(role):
                    st.markdown(f"**{msg['sender']}** <span style='font-size:0.8em; color:#888;'>({msg['time']})</span>", unsafe_allow_html=True)
                    st.markdown(msg["text"])

    user_msg = st.chat_input("메시지를 입력하세요...")
    if user_msg:
        send_room_message(room_name, nickname, user_msg)
        st.rerun()

def render_web_crawling():
    st.title("🌐 실시간 웹 크롤링 및 요약")
    st.caption("DuckDuckGo 검색 결과 파 파싱 & 본문 스크래핑")

    col_kw, col_limit = st.columns([4, 1])
    with col_kw:
        keyword = st.text_input("검색할 키워드를 입력하세요", placeholder="예: 양자컴퓨터 최신 기술 동향")
    with col_limit:
        limit_count = st.selectbox("수집 페이지 수", [3, 5, 7], index=0)

    if st.button("웹 크롤링 시작", use_container_width=True):
        if not keyword.strip():
            st.warning("검색 키워드를 입력해주세요.")
            return

        with st.spinner("검색 결과 수집 및 페이지 본문 파싱 중..."):
            res = perform_search_and_scrape(keyword, limit=limit_count)

        if not res.get("success"):
            st.error(res.get("error"))
        else:
            results = res.get("results", [])
            for idx, item in enumerate(results, start=1):
                with st.container(border=True):
                    c_title, c_btn = st.columns([5, 2])
                    with c_title:
                        st.markdown(f"### {idx}. {item['title']}")
                    with c_btn:
                        st.link_button("🔗 새 창에서 원본 열기", item["url"], use_container_width=True)

                    st.caption(f"출처: `{item['url']}`")
                    st.text_area("스크래핑된 본문 내용", value=item["body"], height=160, key=f"crawl_{idx}")

def render_web_macro():
    st.title("🤖 웹 매크로 자동화 (Selenium)")
    st.caption("새 크롬 브라우저 창 팝업 및 구글 이미지 순차 클릭 매크로")

    col_kw, col_cnt = st.columns([4, 1])
    with col_kw:
        macro_keyword = st.text_input("매크로 검색어", placeholder="예: 고양이")
    with col_cnt:
        click_count = st.number_input("클릭할 이미지 개수", min_value=1, max_value=20, value=10)

    if st.button("🚀 새 브라우저 창 열고 매크로 실행", use_container_width=True):
        if not macro_keyword.strip():
            st.warning("검색어를 입력해주세요.")
            return

        with st.spinner("새 크롬 브라우저 창을 띄워 매크로 동작 중..."):
            res = run_google_image_macro(macro_keyword, max_clicks=int(click_count))

        if not res.get("success"):
            st.error(f"매크로 실패: {res.get('error')}")
        else:
            st.success("매크로 실행이 완료되었습니다.")

        with st.expander("매크로 진행 로그 확인", expanded=True):
            for log in res.get("logs", []):
                st.write(log)

def render_google_map_ui():
    st.title("🗺️ 구글 지도 (Google Maps)")
    st.caption("API 키 등록 없는 임베드 지도 및 위치 검색")

    col_loc, col_search = st.columns([2, 3])
    with col_loc:
        selected = st.selectbox("주요 지역 선택", list(MAP_LOCATIONS.keys()))
        target_place = MAP_LOCATIONS[selected]
    with col_search:
        custom_search = st.text_input("직접 장소 검색 (입력 시 우선 적용)", placeholder="예: 서울역, 도쿄역, 에펠탑")
        if custom_search.strip():
            target_place = custom_search.strip()

    render_google_map(target_place, height=650)

def render_hf_chatbot():
    st.title("🤖 HuggingFace 챗봇")
    
    if "hf_messages" not in st.session_state:
        st.session_state.hf_messages = []

    for msg in st.session_state.hf_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("메시지를 입력하세요"):
        st.session_state.hf_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                response = get_hf_response(st.session_state.hf_messages)
                st.markdown(response)
        st.session_state.hf_messages.append({"role": "assistant", "content": response})

def main():
    st.sidebar.title("🛠️ Multitool Hub")
    selected = st.sidebar.radio(
        "카테고리 선택",
        [
            "🎬 영화 박스오피스", 
            "🎵 빌보드 차트", 
            "📰 뉴스 헤드라인", 
            "📈 주가 시세", 
            "🔥 급상승 트렌드", 
            "🌤️ 주간 날씨", 
            "🛡️ URL 보안 검사",
            "🖥️ PC 네트워크 보안",
            "🎨 그림판",
            "📷 이미지 OCR",
            "🎨 이미지 색상 추출",
            "🎙️ 음성 인식 (Whisper)",
            "🎙️ 음성 인식 (SpeechRecognition)",
            "🔊 텍스트 음성 변환 (TTS)",
            "💬 라이브챗",
            "🌐 웹 크롤링",
            "🤖 웹 매크로",
            "🗺️ 구글 지도",
            "🤖 HuggingFace 챗봇",
            "📝 DB 연동 메모장",
            "📈 DB 연동 주식"
        ]
    )
    
    st.sidebar.divider()
    if st.sidebar.button("🔄 캐시 강제 새로고침"):
        st.cache_data.clear()
        st.rerun()

    if selected == "🎬 영화 박스오피스":
        render_movies()
    elif selected == "🎵 빌보드 차트":
        render_billboard()
    elif selected == "📰 뉴스 헤드라인":
        render_news()
    elif selected == "📈 주가 시세":
        render_stocks()
    elif selected == "🔥 급상승 트렌드":
        render_trends()
    elif selected == "🌤️ 주간 날씨":
        render_weather()
    elif selected == "🛡️ URL 보안 검사":
        render_security()
    elif selected == "🖥️ PC 네트워크 보안":
        render_pc_security()
    elif selected == "🎨 그림판":
        render_paint()
    elif selected == "📷 이미지 OCR":
        render_ocr()
    elif selected == "🎨 이미지 색상 추출":
        render_color_extract()
    elif selected == "🎙️ 음성 인식 (Whisper)":
        render_audio_stt()
    elif selected == "🎙️ 음성 인식 (SpeechRecognition)":
        render_speech_recognition()
    elif selected == "🔊 텍스트 음성 변환 (TTS)":
        render_tts()
    elif selected == "💬 라이브챗":
        render_live_chat()
    elif selected == "🌐 웹 크롤링":
        render_web_crawling()
    elif selected == "🤖 웹 매크로":
        render_web_macro()
    elif selected == "🗺️ 구글 지도":
        render_google_map_ui()
    elif selected == "🤖 HuggingFace 챗봇":
        render_hf_chatbot()
    elif selected == "📝 DB 연동 메모장":
        render_todo_ui()
    elif selected == "📈 DB 연동 주식":
        render_stock_game()

if __name__ == "__main__":
    main()