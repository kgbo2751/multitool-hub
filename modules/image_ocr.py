import numpy as np
import cv2
import easyocr
import streamlit as st

@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(["ko", "en"], gpu=False)

def extract_text_from_bytes(file_bytes: bytes):
    try:
        reader = get_ocr_reader()
        np_img = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"success": False, "error": "이미지 디코딩 실패"}

        results = reader.readtext(img, detail=0)
        return {
            "success": True,
            "text": "\n".join(results) if results else "인식된 글자가 없습니다."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}