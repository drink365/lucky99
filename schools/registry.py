SCHOOLS = {
    "west_astrology": {"name":"西洋占星（本命盤）","desc":"以太陽星座給出今日關鍵建議（MVP）。","requires":["birth_date"],"tone":"占星"},
    "tarot": {"name":"塔羅（單張）","desc":"抽 1 張，直覺給你當下提醒。","requires":["question"],"tone":"宇宙"},
    "ziwei": {"name":"紫微斗數","desc":"以命宮三方四正綜觀人生格局與流年（預留）。","requires":["birth_date","birth_time","gender"],"tone":"心理"},
    "bazi": {"name":"四柱八字（子平）","desc":"日主強弱、十神喜忌（預留）。","requires":["birth_date","birth_time"],"tone":"心理"},
    "iching": {"name":"易經卜卦","desc":"起卦解讀當下變化（預留）。","requires":["question"],"tone":"宇宙"},
    "lifepath": {"name":"生命靈數","desc":"由生日推導 1–9 對應性格與任務。","requires":["birth_date"],"tone":"心理"},
}
