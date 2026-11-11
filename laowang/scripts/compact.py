"""把逐字稿壓成每 60 秒一段, 去除重複短句, 供萃取閱讀.

用法: python compact.py <slug>   輸出到 stdout
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINE = re.compile(r"\[(\d+):(\d\d):(\d\d)\] (.*)")


def main(slug):
    src = ROOT / "transcripts" / f"{slug}.txt"
    out, buf, cur, prev = [], [], None, None
    for line in src.read_text(encoding="utf-8").splitlines():
        m = LINE.match(line)
        if not m:
            if line.startswith("#"):
                out.append(line)
            continue
        h, mi, s, text = m.groups()
        sec = int(h) * 3600 + int(mi) * 60 + int(s)
        block = sec // 60
        if text == prev:
            continue
        prev = text
        if cur is None or block != cur:
            if buf:
                out.append(f"[{cur:02d}m] " + " ".join(buf))
            buf, cur = [], block
        buf.append(text)
    if buf:
        out.append(f"[{cur:02d}m] " + " ".join(buf))
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
