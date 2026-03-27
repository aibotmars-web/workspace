# 幣圈內容生成工具箱

## 無需 API Key 即可使用的工具

### 1. Polymarket 預測市場查詢
```bash
node ~/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs search "比特幣"
node ~/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs search "Trump"
node ~/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs events --tag=politics
```

### 2. YouTube 內容獲取
```bash
# 搜尋影片
node ~/.openclaw/workspace/skills/youtube-full/youtube-full.mjs search "比特幣 教學"

# 獲取字幕
node ~/.openclaw/workspace/skills/youtube-full/youtube-full.mjs transcript "YouTube影片ID"
```

### 3. 瀏覽器自動化（生成圖片/截圖）
使用 `browser` 工具：
- 截取網頁截圖
- 自動化操作（點擊、輸入）

### 4. GIF 搜尋
```bash
node ~/.openclaw/workspace/skills/gifgrep/gifgrep.mjs "比特幣"
```

### 5. 影片工具
```bash
# 截取影片幀
node ~/.openclaw/workspace/skills/video-frames/video-frames.mjs --url "影片URL" --timestamp 10
```

---

## 常用 RSS 訂閱（無需 API）

### 幣圈新聞
- CoinDesk: `https://www.coindesk.com/feed/`
- CoinTelegraph: `https://cointelegraph.com/rss`
- Yahoo Finance (加密): `https://finance.yahoo.com/rss/`

---

## 工作流程

1. **抓新聞** → 用 web_fetch 或瀏覽器抓取幣圈新聞
2. **查市場** → 用 polymarket 查詢相關預測市場概率
3. **生成內容** → 參考上述格式生成 Carousel
4. **發布** → 用 bird (X/Twitter) 發布
