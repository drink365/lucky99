def calc_life_path(date_obj):
    if not date_obj: return None
    s = "".join([c for c in date_obj.strftime("%Y%m%d") if c.isdigit()])
    n = sum(int(c) for c in s)
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n
LIFE_MEANINGS = {
    1:"領導與開創。今日適合主動提案、做決策。",
    2:"協作與傾聽。適合溝通協調、拉近關係。",
    3:"表達與創意。適合寫作發言、內容創作。",
    4:"制度與穩定。適合收斂心神、完成待辦。",
    5:"變化與冒險。適合嘗試新方法或新路線。",
    6:"責任與關懷。適合關心家人夥伴、經營信任。",
    7:"洞察與學習。適合閱讀研究、安靜思考。",
    8:"目標與成果。適合衝刺 KPI、談判資源。",
    9:"願景與助人。適合公益、分享、回饋社群。",
}
def analysis(birth_date):
    n = calc_life_path(birth_date)
    if not n: return "請輸入生日以計算生命靈數。"
    meaning = LIFE_MEANINGS.get(n,"")
    return f"你的生命靈數是 **{n}**：{meaning}\n\n本月建議：聚焦一件能讓你增加 {meaning[:2]} 的行動。"
