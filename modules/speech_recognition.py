import os
import tempfile
import speech_recognition as sr

def recognize_speech_from_audio(uploaded_file, language: str = "ko-KR"):
    temp_path = None
    try:
        suffix = os.path.splitext(uploaded_file.name)[1] if hasattr(uploaded_file, "name") else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_path = temp_audio.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language=language)
            return {"success": True, "text": text}
        except sr.UnknownValueError:
            return {"success": False, "error": "음성을 인식하지 못했습니다."}
        except sr.RequestError as e:
            return {"success": False, "error": f"구글 음성 인식 API 요청 실패: {e}"}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)