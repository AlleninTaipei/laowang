"""從頻道清單篩選【老王不只三分鐘】2023-2026 集數, 建立/合併 batch-status.json."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "_channel_raw.txt"
STATUS = ROOT / "batch-status.json"
YEARS = {"2023", "2024", "2025", "2026"}
TAG = "【老王不只三分鐘】"
DATE_RE = re.compile(r"(20\d\d)/(\d{1,2})/(\d{1,2})")


def main():
    old = {}
    if STATUS.exists():
        old = {e["id"]: e for e in json.loads(STATUS.read_text(encoding="utf-8"))["items"]}

    items, skipped = [], []
    for line in RAW.read_text(encoding="utf-8").splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        vid, dur, title = parts
        if TAG not in title:
            continue
        m = DATE_RE.search(title)
        if not m:
            skipped.append({"id": vid, "title": title, "reason": "標題無日期"})
            continue
        y, mo, d = m.groups()
        if y not in YEARS:
            continue
        date = f"{y}-{int(mo):02d}-{int(d):02d}"
        base = {
            "id": vid,
            "date": date,
            "title": title.replace(TAG, "").strip(),
            "duration": int(float(dur)) if dur not in ("NA", "") else None,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "slug": f"{date}_{vid}",
            "transcript": "pending",
            "note": "pending",
            "error": None,
        }
        if vid in old:
            for k in ("transcript", "note", "error"):
                base[k] = old[vid].get(k, base[k])
        items.append(base)

    items.sort(key=lambda e: (e["date"], e["id"]))
    STATUS.write_text(
        json.dumps({"series": "老王不只三分鐘", "channel_id": "UCvnLmiWt_zIVIh0zUm_j4Hw",
                    "range": "2023-2026", "items": items, "excluded": skipped},
                   ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"items={len(items)} excluded={len(skipped)} first={items[0]['date']} last={items[-1]['date']}")


if __name__ == "__main__":
    sys.exit(main())
