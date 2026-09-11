import os
from PIL import Image

UPLOAD_FOLDER = "Paint"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_drawing_image(image_data, file_name: str = "drawing.png"):
    try:
        img = Image.fromarray(image_data.astype("uint8"))
        save_path = os.path.join(UPLOAD_FOLDER, file_name)
        img.save(save_path)
        return {"success": True, "path": save_path}
    except Exception as e:
        return {"success": False, "error": str(e)}