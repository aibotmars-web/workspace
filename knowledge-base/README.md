# YouTube 專家知識庫追蹤系統

## 檔案結構

```
knowledge-base/
├── tracker.json          # 主資料庫（追蹤所有頻道狀態）
├── sync.py               # 同步腳本（每日執行）
├── summaries/            # 影片摘要存放處
│   ├── Dr.HuangAmin/
│   ├── Dr.Hu_talk/
│   └── ...
└── README.md
```

## 使用方式

### 1. 手動同步（抓取新影片）
```bash
cd /Users/marsbot/.openclaw/workspace/knowledge-base
python3 sync.py
```

### 2. 查看狀態
```bash
cat tracker.json | jq '.'
```

### 3. 查看特定頻道
```bash
cat tracker.json | jq '.channels[0]'
```

## 追蹤內容

每個頻道記錄：
- ✅ 頻道總影片數
- ✅ 已處理影片數
- ✅ 最後檢查時間
- ✅ 影片清單（標題、網址、日期）
- ✅ 字幕內容
- ✅ 摘要狀態

## 更新紀錄

查看 `tracker.json` 中的 `update_log` 陣列：
- 日期
- 動作類型
- 更新頻道數
- 新增影片數

## 自動執行（可選）

加入 crontab，每日 09:00 自動同步：
```bash
0 9 * * * cd /Users/marsbot/.openclaw/workspace/knowledge-base && python3 sync.py >> sync.log 2>&1
```

## 與 Google Sheets 對照

| ID | 頻道名稱 | 帳號 |
|----|----------|------|
| 1 | 阿銘師x針還傳 | @Dr.HuangAmin |
| 2 | 胡乃文開講 | @Dr.Hu_talk |
| 3 | 柏格醫生中文 | @drbergchinese |
| 4 | 周慕姿放心說 | @muerstalk |
| 5 | 松明講心理 | @SongMing |
| 6 | Dr. Harvey不廢話 | @DrHarveyTalk |
| 7 | 初日醫學 | @Cofit211 |
| 8 | 泛科學 PanSci | @PanScitw |
| 9 | 泛科學院 | @panscischool |

## 注意事項

- 只抓字幕，不下載影片（省空間）
- 字幕限制 5000 字元
- 每個頻道最多抓 20 部影片清單
- 新影片會自動加入、清單頂部
