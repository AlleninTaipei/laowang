"""抽樣 v2.

節目結構: 週一, 週四為約 20 分鐘的總經節目. 週二, 週五為約 40 分鐘的技術盤面節目.
- tech: 每兩個 ISO 週取一集技術盤面 (該週第一個週二或週五)
- macro: 每月取一集總經 (該月第一個週一或週四)
- key:<名稱>: 關鍵行情期間全部集數
- kept: 已轉錄但不符合新規則的集數, 保留
在 batch-status.json 每個 item 寫入 sample 欄位, 未選中為 null.
"""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS = ROOT / "batch-status.json"

KEY_PERIODS = {
    "2024-07 高點至 0805 崩跌": ("2024-07-10", "2024-08-23"),
    "2025-04 對等關稅崩跌": ("2025-03-24", "2025-05-09"),
    "2026-10 至 11 修正與國安基金": ("2026-10-01", "2026-11-30"),
}
TECH_DAYS = {1, 4}
MACRO_DAYS = {0, 3}


def main():
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    items = data["items"]
    tech_weeks, macro_months = set(), set()
    for e in items:  # 依日期排序
        d = dt.date.fromisoformat(e["date"])
        old = e.get("sample")
        e["sample"] = None
        for name, (a, b) in KEY_PERIODS.items():
            if a <= e["date"] <= b:
                e["sample"] = f"key:{name}"
        if e["sample"]:
            continue
        y, w, _ = d.isocalendar()
        wd = d.weekday()
        if wd in TECH_DAYS and w % 2 == 0 and (y, w) not in tech_weeks:
            tech_weeks.add((y, w))
            e["sample"] = "tech"
        elif wd in MACRO_DAYS and (d.year, d.month) not in macro_months:
            macro_months.add((d.year, d.month))
            e["sample"] = "macro"
        elif old and (ROOT / "transcripts" / f"{e['slug']}.txt").exists():
            e["sample"] = "kept"
    data["sampling"] = {"version": 2, "rule": __doc__.strip().splitlines()[0], "key_periods": KEY_PERIODS}
    STATUS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    sel = [e for e in items if e["sample"]]
    hours = sum(e["duration"] or 0 for e in sel) / 3600
    todo = [e for e in sel if not (ROOT / "transcripts" / f"{e['slug']}.txt").exists()]
    todo_h = sum(e["duration"] or 0 for e in todo) / 3600
    kinds = {}
    for e in sel:
        k = e["sample"].split(":")[0]
        kinds[k] = kinds.get(k, 0) + 1
    print(f"sample={len(sel)} audio={hours:.1f}h kinds={kinds} todo={len(todo)} todo_audio={todo_h:.1f}h")


if __name__ == "__main__":
    main()
