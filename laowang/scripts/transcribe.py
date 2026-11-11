"""下載音訊並以 faster-whisper 轉錄, 可中斷續跑.

用法: python transcribe.py [--limit N] [--newest-first] [--model small]
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from faster_whisper import WhisperModel
import opencc

ROOT = Path(__file__).resolve().parent.parent
STATUS = ROOT / "batch-status.json"
AUDIO = ROOT / "_audio"
OUT = ROOT / "transcripts"
YTDLP = "yt-dlp"
PROMPT = "以下是台灣股市分析節目「老王不只三分鐘」, 繁體中文. 台積電, 聯發科, 國巨, 0050, 均線, 季線, 月線, 翻多, 翻空, 突破, 跌破, 支撐, 壓力."


def load():
    return json.loads(STATUS.read_text(encoding="utf-8"))


def save_item(item):
    # 每次重新讀檔再寫入, 允許多個程序分工
    data = load()
    for e in data["items"]:
        if e["id"] == item["id"]:
            e.update({k: item[k] for k in ("transcript", "error")})
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(STATUS)


AUDIO_EXT = (".m4a", ".webm", ".opus", ".mp4")


def find_audio(vid):
    for f in AUDIO.glob(f"{vid}.*"):
        if f.suffix in AUDIO_EXT:
            return f
    return None


def download(vid):
    """下載音訊. 若 prefetch.py 正在下載 (有 .lock), 等它完成."""
    lock = AUDIO / f"{vid}.lock"
    while lock.exists():
        time.sleep(10)
    f = find_audio(vid)
    if f:
        return f
    lock.write_text("transcribe", encoding="utf-8")
    try:
        r = fetch(vid)
    finally:
        lock.unlink(missing_ok=True)
    f = find_audio(vid)
    if r.returncode != 0 or not f:
        raise RuntimeError(f"download failed: {r.stderr.strip()[-300:]}")
    return f


def fetch(vid):
    cmd = [YTDLP, "-q", "--no-warnings", "--js-runtimes", "node", "-N", "4",
           "-f", "bestaudio[ext=m4a]/bestaudio",
           "-o", str(AUDIO / "%(id)s.%(ext)s"), f"https://www.youtube.com/watch?v={vid}"]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def decode(path):
    """解碼為 16kHz mono float32 (避開 faster-whisper 與新版 PyAV 的不相容)."""
    import av
    import numpy as np
    chunks = []
    with av.open(str(path)) as c:
        rs = av.AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in c.decode(audio=0):
            for f in rs.resample(frame):
                chunks.append(f.to_ndarray().reshape(-1))
        for f in rs.resample(None):
            chunks.append(f.to_ndarray().reshape(-1))
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def fmt(t):
    t = int(t)
    return f"{t // 3600:d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--newest-first", action="store_true")
    ap.add_argument("--model", default="small")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--shard", default="0/1", help="i/n, 多程序分工")
    ap.add_argument("--sample-only", action="store_true", help="只處理 sample 欄位非空的集數")
    a = ap.parse_args()
    si, sn = map(int, a.shard.split("/"))

    cc = opencc.OpenCC("s2tw")
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads)
    items = [e for e in load()["items"] if e["transcript"] in ("pending", "retryable")]
    if a.sample_only:
        items = [e for e in items if e.get("sample")]
    if a.newest_first:
        items.reverse()
    items = [e for i, e in enumerate(items) if i % sn == si]
    if a.limit:
        items = items[: a.limit]
    print(f"todo={len(items)}", flush=True)

    for e in items:
        out = OUT / f"{e['slug']}.txt"
        if out.exists():
            e["transcript"], e["error"] = "completed", None
            save_item(e)
            continue
        t0 = time.time()
        try:
            audio = download(e["id"])
            segs, info = model.transcribe(decode(audio), language="zh", initial_prompt=PROMPT,
                                          vad_filter=True, beam_size=1)
            lines = [f"# {e['title']}", f"# {e['url']}", f"# date={e['date']}", ""]
            for s in segs:
                lines.append(f"[{fmt(s.start)}] {cc.convert(s.text.strip())}")
            out.write_text("\n".join(lines) + "\n", encoding="utf-8")
            audio.unlink(missing_ok=True)
            e["transcript"], e["error"] = "completed", None
            print(f"ok {e['slug']} {time.time() - t0:.0f}s / {info.duration:.0f}s audio", flush=True)
        except Exception as ex:  # noqa: BLE001
            e["transcript"], e["error"] = "retryable", str(ex)[:500]
            print(f"fail {e['slug']}: {ex}", flush=True)
        save_item(e)


if __name__ == "__main__":
    sys.exit(main())
