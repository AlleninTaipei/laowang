"""Build laowang/README.md index from batch-status.json and notes/."""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "batch-status.json").read_text(encoding="utf-8"))
items = sorted([e for e in d["items"] if e.get("sample")], key=lambda e: e["date"])
cat = {"tech": 0, "macro": 0, "key": 0, "kept": 0}
rows = {}
for e in items:
    s = e["sample"]
    k = "key" if s.startswith("key") else s
    cat[k] = cat.get(k, 0) + 1
    note = root / "notes" / f"{e['slug']}.md"
    title = e["title"]
    if note.exists():
        h1 = note.read_text(encoding="utf-8").splitlines()[0]
        title = re.sub(r"^#\s*", "", h1)
        title = re.sub(r"\s*\(\d{4}-\d{2}-\d{2}\)\s*$", "", title)
    label = s.replace("key:", "關鍵: ").strip()
    rows.setdefault(e["date"][:4], []).append(
        f"| {e['date']} | [{title}](notes/{e['slug']}.md) | {label} | [影片]({e['url']}) |")
done = sum(1 for e in items if e["note"] == "completed")
out = [
    "# 老王不只三分鐘: 筆記索引",
    "",
    f"- 範圍: 2023-01 至 2026-11, 抽樣 {len(items)} 集 (全部 {len(d['items'])} 集). 筆記完成 {done} 集.",
    f"- 抽樣類別: 技術盤面 tech {cat.get('tech',0)} 集, 總經 macro {cat.get('macro',0)} 集, 關鍵行情 key {cat.get('key',0)} 集, 保留 kept {cat.get('kept',0)} 集.",
    "- 關鍵行情: 2024/07 至 08 崩跌, 2025/03 至 05 對等關稅崩跌, 2026/10 至 11 修正與國安基金.",
    "- 內容依據: 本機 Whisper small 轉錄 (影片無字幕), 專有名詞依上下文校正, 誤字對照見 [glossary.md](glossary.md).",
    "- 方法論彙整: [methodology.md](methodology.md). 每集筆記把可泛化方法與當期個股看法分開.",
    "- 本資料為單一分析師的公開節目整理, 不是投資建議.",
    "",
]
for y in sorted(rows):
    out += [f"## {y} ({len(rows[y])} 集)", "", "| 日期 | 標題 | 類別 | 原片 |", "| --- | --- | --- | --- |"] + rows[y] + [""]
(root / "README.md").write_text("\n".join(out), encoding="utf-8")
print("README rows:", sum(len(v) for v in rows.values()))
