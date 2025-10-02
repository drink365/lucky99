import os, csv, shutil, pandas as pd
from typing import Dict, List

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DRAW_LOG   = os.path.join(DATA_DIR, "draw_log.csv")
SIGNIN_LOG = os.path.join(DATA_DIR, "signin_log.csv")

COLS: List[str] = [
    "ts","user","system","school","fortune","note","task","school_key","inputs"
]

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
