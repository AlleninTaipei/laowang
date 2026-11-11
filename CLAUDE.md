# 老王策略 Skill 專案

目標: 從「老王不只三分鐘」2023 至 2026 抽樣 185 集萃取操作方法論, 最後做成 `.claude/skills/laowang-strategy/` Skill.

節目結構: 週一, 週四是約 20 分鐘的總經節目 (解讀外資報告). 週二, 週五是約 40 分鐘的技術盤面節目 (操作規則的主要來源).
抽樣 v2 (`scripts/select_sample.py`): 技術盤面每兩週一集 (tech), 總經每月一集 (macro), 三段關鍵行情全取 (key), 已轉錄者保留 (kept).

## 目錄

- `laowang/batch-status.json`: 613 集清單. `sample` 非空代表在樣本內, `transcript` / `note` 為處理狀態.
- `laowang/transcripts/`: Whisper 逐字稿 (誤字多).
- `laowang/notes/`: 每集萃取筆記. 範本: `notes/2026-11-10_pNkrHmBzZ9c.md`.
- `laowang/glossary.md`: 轉錄誤字對照, 遇到新誤字就補.
- `laowang/scripts/`: `transcribe.py` 轉錄, `compact.py` 壓縮閱讀, `status.py` 進度.
- Python venv: `.venv` (faster-whisper). 系統 Python 用於 `status.py`, `compact.py`.

## 續跑流程 (使用者說 "繼續萃取" 時)

1. 檢查轉錄程序是否還在跑: `tasklist | grep python` 與 `laowang/logs/shard*.log`, `prefetch.log`. 沒在跑且仍有未轉錄樣本, 就用 venv python 以 Start-Process (WorkingDirectory=laowang, WindowStyle Hidden, 輸出導到 logs/) 重新啟動: `scripts\transcribe.py --sample-only --threads 8 --shard i/3` (i=0,1,2, 由舊到新) 加上 `scripts\prefetch.py --buffer 9 --oldest-first`. 兩者順序必須一致, 否則預先下載的緩衝會塞滿而停住. 下載必須帶 `-N 4`, 否則每集要 10 分鐘以上.
2. `cd laowang && PYTHONUTF8=1 python scripts/status.py 5` 取得下一批.
3. 每集: `python scripts/compact.py <slug>` 讀取, 依範本寫 `notes/<slug>.md`. 方法論和當期個股看法分開, 時間戳連結用 `&t=秒數s`.
4. 每批 5 集後再跑一次 `status.py` 更新狀態.
5. `laowang/methodology.md` 是逐步更新的彙整稿 (規則後標註出處日期). 每處理一批新年份的筆記, 就把新規則或演變補進去.
6. 全部筆記完成後: 定稿 methodology.md (規則, 演變, 關鍵行情驗證), 產生 `laowang/README.md` 索引, 最後建立 Skill.

## 目前狀態 (2026-11-11)

185 集全部完成. Skill 在 `.claude/skills/laowang-strategy/`. 修改 `laowang/methodology.md` 後, 同步複製到 Skill 的 `references/methodology.md`; 筆記有增減時執行 `python scripts/build_readme.py` 重建索引.

## 撰寫慣例

依使用者全域設定: 不用粗體, 不用 emoji, 半形標點後加空格.
