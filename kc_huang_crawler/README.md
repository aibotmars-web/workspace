# 🕵️ 黃國昌 YouTube 爬蟲

## 📌 說明

此爬蟲用於分析黃國昌 YouTube 頻道 (@KC-Huang) 的影片內容，特別關注以下重大弊案：

- **超思雞蛋** - 進口雞蛋爭議
- **台鹽綠能** - 光電弊案
- **聯合再生** - 再生能源弊案
- **88會館** - 地下匯兌洗錢案
- **imb詐騙** - 投資詐騙案

## 🚀 使用方式

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 執行爬蟲

```bash
python youtube_crawler.py
```

### 3. 查看進度報告

爬蟲完成後，在瀏覽器中打開：

```
reports/progress.html
```

## 📊 輸出內容

爬蟲會產生以下輸出：

- `data/crawl_state.json` - 所有爬取資料的 JSON 檔案
- `reports/progress.html` - 互動式 HTML 進度報告
- `data/*.vtt` - 下載的字幕檔案

## 🎯 功能特點

1. **自動取得頻道所有影片清單**
2. **下載影片字幕**（中文優先）
3. **關鍵字匹配** - 自動識別與弊案相關的影片
4. **HTML 進度報告** - 即時顯示爬取狀態
5. **錯誤處理** - 記錄失敗的影片以便重試

## ⚠️ 注意事項

- YouTube 有 API 請求限制，爬蟲已內建延遲機制
- 字幕下載需要網路連線
- 大量影片可能需要數小時才能完成

## 📝 自定義設定

如需修改目標頻道或關鍵字，編輯 `youtube_crawler.py` 中的：

- `CHANNEL_URL` - 目標頻道網址
- `KEYWORDS` - 弊案關鍵字清單
- `languages` - 要下載的字幕語言
