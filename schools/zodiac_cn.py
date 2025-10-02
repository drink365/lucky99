SHENGXIAO_ORDER = ["鼠","牛","虎","兔","龍","蛇","馬","羊","猴","雞","狗","豬"]
SHENGXIAO_YEAR0 = 2020  # 鼠
ASPECTS = ["事業","財運","感情","健康"]
TEMPLATES = {
    "鼠":"主打「穩」：把注意力放在基本功與現金流。",
    "牛":"貴人運浮現，合作是今年的關鍵字。",
    "虎":"聚焦一個戰場，避免分散能量。",
    "兔":"維護關係品質，溫柔即力量。",
    "龍":"舞台感上升，勇於表現會被看見。",
    "蛇":"學習曲線陡峭，但回報也更高。",
    "馬":"移動與旅行帶來機會，主動出擊。",
    "羊":"節奏與健康要優先，慢即是快。",
    "猴":"資訊是你的優勢，勤交流多突破。",
    "雞":"秩序與紀律帶來穩定成長。",
    "狗":"守成中求變，嘗試新工具。",
    "豬":"關係與資源整合，迎向豐盛。",
}
def zodiac_of(birth_date):
    if not birth_date: return None
    y = birth_date.year
    idx = (y - SHENGXIAO_YEAR0) % 12
    return SHENGXIAO_ORDER[idx]
def analysis(birth_date, year=2025):
    z = zodiac_of(birth_date)
    if not z: return "請輸入生日以判斷生肖。"
    base = TEMPLATES.get(z, "今年以穩為主，循序漸進。")
    lines = [f"- **{aspect}**：{base}" for aspect in ASPECTS]
    return f"你的生肖是 **{z}**。\n**{year} 流年重點**：\n" + "\n".join(lines)
