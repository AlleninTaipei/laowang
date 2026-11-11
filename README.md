# 老王策略 Skill

從 YouTube 節目 "老王不只三分鐘" 2023 至 2026 年抽樣 185 集, 萃取台股操作方法論, 做成 Claude Code Skill.

## 內容

- `.claude/skills/laowang-strategy/`: Skill 本體. 在此專案中開啟 Claude Code, 提到老王或問均線, 持股水位等問題即會載入.
- `laowang/methodology.md`: 方法論彙整, 每條規則附出處日期.
- `laowang/README.md`: 185 集筆記索引.
- `laowang/notes/`: 每集筆記, 方法論與當期個股看法分開, 附影片時間戳連結.
- `laowang/glossary.md`: 轉錄誤字對照.
- `laowang/scripts/`: 抽樣, 轉錄 (faster-whisper), 進度與索引腳本.

逐字稿與音檔不收錄於此 repo.

## 在 claude.ai 網頁版使用

網頁版不會讀取 repo 內的 `.claude/skills/`, 需要把 Skill 打包成 ZIP 上傳. 本 repo 已附打包好的檔案 `dist/laowang-strategy.zip`.

1. 下載 ZIP: 在 GitHub 開啟 `dist/laowang-strategy.zip`, 按 "Download raw file". 不要解壓縮.
2. 開啟 claude.ai, 進入 設定 (Settings) > 功能 (Capabilities).
3. 確認已開啟 "程式碼執行與檔案建立" (Code execution and file creation). Skills 需要這項功能.
4. 在 Skills 區塊按 "上傳技能" (Upload skill), 選擇剛下載的 ZIP.
5. 上傳後確認 `laowang-strategy` 為開啟狀態.
6. 開新對話, 直接問 "用老王的方法看, 台積電跌破月線該怎麼辦?", Claude 會自動載入這個 Skill.

說明:

- Skills 需要付費方案 (Pro, Max, Team, Enterprise). Team 與 Enterprise 可能需要管理員先開放. 介面名稱可能隨版本調整.
- 網頁版只會載入 ZIP 內的 Skill 檔案 (`SKILL.md` 與 `references/`), 不包含 185 集筆記. 若想讓 Claude 引用個別集數, 可建立一個 Project, 把 `laowang/notes/` 中需要的筆記上傳為專案知識.
- 修改 Skill 後要重新打包: ZIP 內需以 `laowang-strategy/` 資料夾為最上層, 裡面放 `SKILL.md` 與 `references/`.

## 聲明

本資料是對單一分析師公開節目的個人整理與摘要, 不代表節目方, 不是投資建議. 內容依本機語音轉錄, 專有名詞可能有誤.
