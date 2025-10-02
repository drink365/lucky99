SCHOOLS = {
    "west_astrology": {"name":"西洋占星（太陽星座）","desc":"依生日判斷太陽星座與本月重點。","requires":["birth_date"],"tone":"占星"},
    "tarot": {"name":"塔羅（單張/三張）","desc":"單張：快速提醒；三張：過去/現在/未來（Pro）。","requires":["question"],"tone":"宇宙"},
    "lifepath": {"name":"生命靈數","desc":"由生日推導 1–9 對應性格與任務。","requires":["birth_date"],"tone":"心理"},
    "zodiac_cn": {"name":"生肖（流年）","desc":"自動對應生肖，輸出今年四大面向建議（Pro+）。","requires":["birth_date"],"tone":"東方"},
    "ziwei": {"name":"紫微斗數（簡版）","desc":"以生日推估命宮性格與本年關鍵提醒（Pro+）。","requires":["birth_date","gender"],"tone":"東方"},
    "bazi": {"name":"八字（五行簡析）","desc":"以生日推四柱簡化，分析五行強弱（Pro+）。","requires":["birth_date","birth_time"],"tone":"東方"},
}
