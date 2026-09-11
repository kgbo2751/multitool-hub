import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def run_google_image_macro(keyword: str, max_clicks: int = 10):
    logs = []
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        logs.append("1. 구글 브라우저 실행 및 접속 완료")
        driver.get("https://www.google.com")

        logs.append(f"2. 키워드 '{keyword}' 자동 입력 및 검색")
        search_box = driver.find_element(By.NAME, "q")
        for char in keyword:
            search_box.send_keys(char)
            time.sleep(0.03)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        logs.append("3. 이미지 탭 탐색 및 이동")
        image_tab = driver.find_element(
            By.XPATH, 
            "//a[contains(., '이미지')] | //div[contains(text(), '이미지')] | //span[contains(text(), '이미지')]"
        )
        image_tab.click()
        time.sleep(2)

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)

        all_imgs = driver.find_elements(By.CSS_SELECTOR, "div#search img, div#rso img, g-img img")
        valid_images = [img for img in all_imgs if img.size.get('width', 0) > 50 and img.size.get('height', 0) > 50]
        logs.append(f"-> 유효 썸네일 {len(valid_images)}개 감지")

        target_count = min(max_clicks, len(valid_images))
        for i in range(target_count):
            img = valid_images[i]
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", img)
                logs.append(f" - [{i+1}/{target_count}] 썸네일 클릭 성공")
                time.sleep(1.2)
            except Exception as e:
                logs.append(f" - [{i+1}/{target_count}] 클릭 실패: {str(e)}")

        logs.append("4. 매크로 작업 완료")
        return {"success": True, "logs": logs}

    except Exception as e:
        return {"success": False, "error": str(e), "logs": logs}