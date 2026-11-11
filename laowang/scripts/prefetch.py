"""預先下載樣本音訊, 讓下載與轉錄並行. 最多緩衝 BUFFER 個檔案.

用法: python prefetch.py [--buffer 9]
與 transcribe.py 以 _audio/<id>.lock 協調, 不會重複下載.
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
OLDEST = "--oldest-first" in sys.argv
from transcribe import AUDIO, OUT, STATUS, fetch, find_audio  # noqa: E402


def pending():
    items = json.loads(STATUS.read_text(encoding="utf-8"))["items"]
    items = [e for e in items if e.get("sample") and e["transcript"] in ("pending", "retryable")
             and not (OUT / f"{e['slug']}.txt").exists()]
    items.sort(key=lambda e: e["date"], reverse=not OLDEST)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--buffer", type=int, default=9)
    ap.add_argument("--oldest-first", action="store_true")
    a = ap.parse_args()
    fails = {}
    while True:
        todo = [e for e in pending() if not find_audio(e["id"])
                and not (AUDIO / f"{e['id']}.lock").exists() and fails.get(e["id"], 0) < 3]
        if not todo:
            print("prefetch: nothing left", flush=True)
            return
        buffered = len([f for f in AUDIO.iterdir() if f.suffix in (".m4a", ".webm", ".opus", ".mp4")])
        if buffered >= a.buffer:
            time.sleep(30)
            continue
        e = todo[0]
        lock = AUDIO / f"{e['id']}.lock"
        lock.write_text("prefetch", encoding="utf-8")
        t0 = time.time()
        try:
            r = fetch(e["id"])
        finally:
            lock.unlink(missing_ok=True)
        if r.returncode != 0 or not find_audio(e["id"]):
            fails[e["id"]] = fails.get(e["id"], 0) + 1
            print(f"prefetch fail {e['slug']}: {r.stderr.strip()[-200:]}", flush=True)
        else:
            print(f"prefetch ok {e['slug']} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
