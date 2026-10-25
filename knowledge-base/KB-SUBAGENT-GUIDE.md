# 知識庫統一追蹤系統

*建立時間：2026-06-09*
*唯一真相來源：`kb-unified-state.json`*

---

## 核心原則

**所有 sub-agent 和腳本必須使用 `kb-state-manager.py` 讀寫進度。**

禁止直接修改 `crawl_state.json`、`channel_stats.json`、`progress.csv` 等舊檔案。

---

## 檔案路徑

| 檔案 | 用途 |
|------|------|
| `kb-unified-state.json` | **唯一真相來源**（Single Source of Truth） |
| `kb-state-manager.py` | 管理器腳本（讀寫進度） |
| `kb-progress.csv` | 進度報告（自動生成） |
| `experts/` | 各頻道的原始字幕檔 |
| `summaries/` | AI 摘要 JSON |

---

## 管理器指令

```bash
# 讀取目前進度
python3 kb-state-manager.py read

# 同步實際檔案數量（從專家目錄）
python3 kb-state-manager.py sync

# 檢查問題
python3 kb-state-manager.py check

# 更新頻道已爬數量
python3 kb-state-manager.py update <channel_id> <count>

# 更新頻道的影片 ID 清單（用於去重）
python3 kb-state-manager.py update_ids <channel_id> '["video1","video2",...]'

# 更新頻道的摘要數量
python3 kb-state-manager.py summary_update <channel_id> <count>

# 生成進度報告 CSV
python3 kb-state-manager.py report
```

---

## 頻道 ID 對照

| ID | 顯示名稱 |
|----|----------|
| `Dr.Hu_talk` | 胡乃文再開 |
| `drbergchinese` | 柏格醫生中文 |
| `muerstalk` | 周慕姿放心說 |
| `panscischool` | 泛科學院 |
| `Cofit211` | Cofit211 |
| `PanScitw` | 泛科學 |
| `SongMing` | 松明讲心理 |
| `Dr.HuangAmin` | Dr.HuangAmin |
| `RealBizChat` | 商談・不廢話（已合併超真實商談）|

---

## 爬蟲工作流程

1. 讀取 `kb-unified-state.json` 取得目前進度
2. 執行爬蟲（`crawl_stable.py`）
3. 爬完後用 `kb-state-manager.py sync` 同步實際檔案數量
4. 用 `kb-state-manager.py update` 更新進度
5. 執行摘要（`summarize_transcripts.py`）
6. 用 `kb-state-manager.py summary_update` 更新摘要數

---

## 已知問題

1. **超真實商談 已停用** — 已合併至 RealBizChat，請勿單獨爬取
2. **摘要嚴重落後** — 已爬 643 部影片，但只有 24 筆摘要（4%）
3. **爬蟲停滯** — 所有頻道上次更新都在 9-22 天前，需要重啟

---

## Cron Jobs

| 名稱 | 排程 | 用途 |
|------|------|------|
| 知識庫爬蟲 | 每天 04:00 | 爬取新影片 |
| 知識庫進度報告 | 每天 10:00 | 發送進度到 TG |