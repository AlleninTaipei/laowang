"""同步筆記狀態並列出下一批待萃取集數.

用法: python status.py [N]   預設列出 5 集
note 狀態以 notes/<slug>.md 是否存在為準.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUS = ROOT / "batch-status.json"


def main(n=5):
    sys.stdout.reconfigure(encoding="utf-8")
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    items = data["items"]
    for e in items:
        if (ROOT / "transcripts" / f"{e['slug']}.txt").exists():
            e["transcript"] = "completed"
        if (ROOT / "notes" / f"{e['slug']}.md").exists():
            e["note"] = "completed"
    tmp = STATUS.with_suffix(".tmp2")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATUS)

    sample = [e for e in items if e.get("sample")]
    tc = Counter(e["transcript"] for e in sample)
    nc = Counter(e["note"] for e in sample)
    print(f"sample={len(sample)} transcript={dict(tc)} note={dict(nc)}")
    ready = [e for e in sample if e["transcript"] == "completed" and e["note"] != "completed"]
    ready.sort(key=lambda e: e["date"], reverse=True)
    print(f"ready_for_note={len(ready)}")
    for e in ready[:n]:
        print(f"{e['slug']}\t{e['sample']}\t{e['title']}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
