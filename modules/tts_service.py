import os
import io

try:
    from gtts import gTTS
except ImportError:
    from gTTS import gTTS

UPLOAD_FOLDER = "TTS"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_speech(text: str, lang: str = "ko", save_to_disk: bool = True):
    try:
        tts = gTTS(text=text, lang=lang)
        
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        saved_path = None
        if save_to_disk:
            saved_path = os.path.join(UPLOAD_FOLDER, "output.mp3")
            with open(saved_path, "wb") as f:
                f.write(mp3_fp.getvalue())

        return {
            "success": True,
            "audio_bytes": mp3_fp.getvalue(),
            "file_path": saved_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}