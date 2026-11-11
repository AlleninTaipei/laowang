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

## 聲明

本資料是對單一分析師公開節目的個人整理與摘要, 不代表節目方, 不是投資建議. 內容依本機語音轉錄, 專有名詞可能有誤.
