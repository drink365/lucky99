import os, csv, shutil, pandas as pd, datetime
from typing import Dict, List, Optional, Tuple

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DRAW_LOG   = os.path.join(DATA_DIR, "draw_log.csv")
SUBS_LOG   = os.path.join(DATA_DIR, "subscriptions.csv")

COLS: List[str] = ["ts","user","system","school","fortune","note","task","school_key","inputs"]
SUBS_COLS = ["user","plan","stripe_customer","stripe_subscription","current_period_end","status","updated_at"]

def safe_read_csv(path: str, cols: List[str]) -> pd.DataFrame:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(path, on_bad_lines="skip", engine="python")
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df
    except Exception:
        try:
            shutil.copy(path, path + ".bak")
        except Exception:
            pass
        return pd.DataFrame(columns=cols)

def append_row(path: str, row: Dict[str, str], cols: List[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists = os.path.exists(path)
    safe_row = {c: row.get(c, "") for c in cols}
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if not exists:
            w.writeheader()
        w.writerow(safe_row)

def upsert_subscription_record(user: str, plan: str, stripe_customer: str, stripe_subscription: str, current_period_end: Optional[int], status: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    items = []
    if os.path.exists(SUBS_LOG):
        with open(SUBS_LOG, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                items.append(row)
    found = False
    for it in items:
        if it.get("user")==user:
            it.update({
                "plan": plan,
                "stripe_customer": stripe_customer or "",
                "stripe_subscription": stripe_subscription or "",
                "current_period_end": str(current_period_end or ""),
                "status": status,
                "updated_at": datetime.datetime.now().isoformat(timespec="seconds")
            })
            found = True
            break
    if not found:
        items.append({
            "user": user,
            "plan": plan,
            "stripe_customer": stripe_customer or "",
            "stripe_subscription": stripe_subscription or "",
            "current_period_end": str(current_period_end or ""),
            "status": status,
            "updated_at": datetime.datetime.now().isoformat(timespec="seconds")
        })
    with open(SUBS_LOG, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUBS_COLS)
        w.writeheader()
        for it in items:
            w.writerow(it)

def get_subscription(user: str) -> str:
    plan, expiry, status = get_subscription_detail(user)
    if status not in ("active","trialing"):
        return "Free"
    if expiry and expiry < int(datetime.datetime.now().timestamp()):
        return "Free"
    return plan or "Free"

def get_subscription_detail(user: str) -> Tuple[str, Optional[int], str]:
    path = SUBS_LOG
    if not os.path.exists(path):
        return "Free", None, "canceled"
    try:
        df = pd.read_csv(path)
        row = df[df["user"]==user].tail(1)
        if row.empty:
            return "Free", None, "canceled"
        plan = str(row["plan"].iloc[0] or "Free")
        status = str(row["status"].iloc[0] or "canceled")
        cpe_raw = row.get("current_period_end")
        expiry_ts = None
        if cpe_raw is not None and not pd.isna(cpe_raw.iloc[0]):
            try:
                expiry_ts = int(float(cpe_raw.iloc[0]))
            except Exception:
                expiry_ts = None
        return plan, expiry_ts, status
    except Exception:
        return "Free", None, "canceled"
