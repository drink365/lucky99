from PIL import ImageFont
import os
FONT_CANDIDATES = [
    "assets/NotoSansTC-Regular.ttf",
    "/mnt/data/NotoSansTC-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
def get_font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()
