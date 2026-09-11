import os
import tempfile
import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model(model_name: str = "base"):
    return whisper.load_model(model_name)

def transcribe_audio_file(uploaded_file):
    temp_path = None
    try:
        model = load_whisper_model("base")
        suffix = os.path.splitext(uploaded_file.name)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_path = temp_audio.name

        result = model.transcribe(temp_path)
        return {
            "success": True,
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)