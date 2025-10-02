SCHOOLS = {
    "west_astrology": {
        "name": "西洋占星（本命盤）",
        "desc": "以行星落宮與相位解讀你的天賦與課題。",
        "requires": ["birth_date", "birth_time", "birth_place"],
        "tone": "占星",
    },
    "tarot": {
        "name": "塔羅（78 張）",
        "desc": "針對具體問題給出象徵與建議，適合短期抉擇。",
        "requires": ["question"],
        "tone": "宇宙",
    },
    "ziwei": {
        "name": "紫微斗數",
        "desc": "以命宮三方四正綜觀人生格局與流年趨勢。",
        "requires": ["birth_date", "birth_time", "gender"],
        "tone": "心理",
    },
    "bazi": {
        "name": "四柱八字（子平）",
        "desc": "以日主強弱、十神喜忌判斷運勢與用神方向。",
        "requires": ["birth_date", "birth_time"],
        "tone": "心理",
    },
    "iching": {
        "name": "易經卜卦",
        "desc": "以起卦時刻或擲銅錢得卦，解讀當下變化。",
        "requires": ["question"],
        "tone": "宇宙",
    },
    "lifepath": {
        "name": "生命靈數",
        "desc": "由生日推導生命靈數 1–9，對應性格與任務。",
        "requires": ["birth_date"],
        "tone": "心理",
    },
}
