HEAVENLY_STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
EARTHLY_BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
STEM_ELEMENT = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
BRANCH_ELEMENT = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
FIVE = ["金","木","水","火","土"]
def sexagenary_of(year:int):
    stem = HEAVENLY_STEMS[(year - 4) % 10]
    branch = EARTHLY_BRANCHES[(year - 4) % 12]
    return stem, branch
def analysis(birth_date, birth_time=None, detail=False):
    if not birth_date: return "請輸入生日（可選填時辰）。"
    stem, branch = sexagenary_of(birth_date.year)
    counts = {e:0 for e in FIVE}
    counts[STEM_ELEMENT[stem]] += 2
    counts[BRANCH_ELEMENT[branch]] += 1
    if birth_date.month in (3,4,5): counts["木"] += 1
    if birth_date.month in (6,7,8): counts["火"] += 1
    if birth_date.month in (9,10,11): counts["金"] += 1
    if birth_date.month in (12,1,2): counts["水"] += 1
    if birth_date.day % 5 == 0: counts["土"] += 1
    strong = sorted(FIVE, key=lambda e: -counts[e])[:2]
    weak = sorted(FIVE, key=lambda e: counts[e])[:1]
    base = f"你的年柱為 **{stem}{branch}**（天干屬{STEM_ELEMENT[stem]}、地支屬{BRANCH_ELEMENT[branch]}）。\n五行傾向：強 → {strong}；較弱 → {weak}。"
    if not detail:
        return base + "\n建議：以強帶弱，例如用 {0} 的優勢去補強 {1} 面向的行動。".format(strong[0], weak[0])
    return base + "\n【詳細版】行動：1) 每週固定補{0}活動 2) 工作選擇避開過多{1}負荷 3) 與互補夥伴協作。".format(weak[0], weak[0])
