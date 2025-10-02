import os, textwrap
from datetime import datetime
from PIL import Image, ImageDraw
from utils.fonts import get_font

def build_share_image(card, out_dir):
    W, H = 1080, 1350
    pad = 64
    img = Image.new("RGB", (W, H), card.get("color_primary","#F2D9B3"))
    draw = ImageDraw.Draw(img)
    font_title = get_font(64)
    font_label = get_font(42)
    font_body  = get_font(40)
    font_meta  = get_font(32)
    # Title
    draw.text((pad, pad), f"幸運99｜{card.get('system','提醒')}", font=font_title, fill=(30,30,30))
    # Blocks
    def block(y, label, content):
        draw.text((pad, y), label, font=font_label, fill=(50,50,50))
        y += 56
        wrapped = textwrap.fill(content or "", width=18)
        draw.multiline_text((pad, y), wrapped, font=font_body, fill=(20,20,20), spacing=8)
        lines = wrapped.count("\n") + 1 if wrapped else 0
        return y + 42*lines + 28
    y = 180
    y = block(y, "籤語", card.get("fortune",""))
    y = block(y, "小語", card.get("note",""))
    y = block(y, "今日任務", card.get("task",""))
    draw.text((pad, H-96), f"{card.get('user','用戶')} · {datetime.now().date()}", font=font_meta, fill=(40,40,40))
    draw.text((W-520, H-96), "© 幸運99 Lucky99", font=font_meta, fill=(40,40,40))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"share_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    img.save(out_path, "PNG")
    return out_path, img
