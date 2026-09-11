import numpy as np
import cv2
from sklearn.cluster import KMeans

def extract_dominant_colors(image_bytes: bytes, k: int = 5):
    try:
        np_img = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "error": "이미지 디코딩 실패"}

        height, width = img.shape[:2]
        new_width = 200
        new_height = int(height * (new_width / width))
        img_small = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        pixels = img_rgb.reshape(-1, 3)

        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(pixels)

        _, counts = np.unique(kmeans.labels_, return_counts=True)
        total_pixels = len(pixels)

        colors_info = []
        for i in range(len(counts)):
            rgb = kmeans.cluster_centers_[i].astype(int)
            hex_code = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()
            percentage = round((counts[i] / total_pixels) * 100, 1)
            colors_info.append({
                "hex": hex_code,
                "rgb": f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})",
                "percent": percentage
            })

        colors_info = sorted(colors_info, key=lambda x: x["percent"], reverse=True)
        return {"success": True, "colors": colors_info}
    except Exception as e:
        return {"success": False, "error": str(e)}