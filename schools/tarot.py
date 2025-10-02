import random
TAROT_CARDS = [
    ("愚者", "自由、開端、天真", "魯莽、分心、遲疑"),
    ("魔術師", "資源到位、主動創造", "力不從心、方向分散"),
    ("女祭司", "直覺、內在智慧", "秘密、壓抑情緒"),
    ("女皇", "豐盛、關懷、創造力", "過度縱容、停滯"),
    ("皇帝", "結構、掌控、權威", "僵化、控制慾"),
    ("教皇", "規範、傳承、學習", "教條、缺乏彈性"),
    ("戀人", "選擇、關係、契合", "猶豫、不一致"),
    ("戰車", "行動、意志、勝利", "衝動、失控"),
    ("力量", "溫柔的力量、自我接納", "自我懷疑、操之過急"),
    ("隱者", "思考、沉澱、內在旅程", "孤立、逃避"),
    ("命運之輪", "轉變、機緣", "不穩定、被動等待"),
    ("正義", "公平、抉擇、真相", "偏頗、失衡"),
    ("吊人", "換位、暫停、犧牲", "拖延、固著"),
    ("死神", "結束與重生", "害怕改變、放不下"),
    ("節制", "協調、節奏、療癒", "失衡、過度"),
    ("惡魔", "慾望、束縛、覺察陰影", "放縱、受困"),
    ("塔", "覺醒、重組", "崩塌、震盪"),
    ("星星", "希望、靈感、療癒", "迷茫、失落"),
    ("月亮", "潛意識、夢境、直覺", "焦慮、誤判"),
    ("太陽", "喜悅、成功、清晰", "自滿、膨脹"),
    ("審判", "覺醒、召喚、復甦", "拖延改變、迴避責任"),
    ("世界", "完成、整合、跨界", "延宕、未竟之事"),
]
def draw_one(seed=None):
    rng = random.Random(seed)
    name, upright, reversed_meaning = rng.choice(TAROT_CARDS)
    reversed_flag = rng.choice([True, False])
    meaning = reversed_meaning if reversed_flag else upright
    pose = "逆位" if reversed_flag else "正位"
    return {"name": name, "pose": pose, "meaning": meaning}
def draw_three(seed=None):
    rng = random.Random(seed)
    picks = rng.sample(TAROT_CARDS, 3)
    out = []
    for i, (name, up, rev) in enumerate(picks):
        reversed_flag = rng.choice([True, False])
        meaning = rev if reversed_flag else up
        pose = "逆位" if reversed_flag else "正位"
        slot = ["過去","現在","未來"][i]
        out.append({"slot": slot, "name": name, "pose": pose, "meaning": meaning})
    return out
def analysis(question: str):
    base = "塔羅是一種以 78 張原型符號反映當下能量的工具。"
    ask = f"你的提問是「{question}」。" if question else "建議先聚焦一個問題（例如：本月合作運勢如何？）。"
    return f"{base}\n{ask}\n接下來你可以抽單張（快速提醒）或三張（過去/現在/未來）。"
