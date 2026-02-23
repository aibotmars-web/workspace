# 瀏覽器自動化 (Browser Automation)

## 工具
- peekaboo - 主要瀏覽器自動化工具

## 功能
- 截圖、分析、點擊、輸入、滾動
- 自動化網頁操作
- 爬蟲數據

## 指令範例

```bash
# 截圖
peekaboo image --path screenshot.png

# 點擊座標
peekaboo click --coords 100,200

# 輸入文字
peekaboo type "hello"

# 滾動頁面
peekaboo scroll --direction down --amount 6

# 分析截圖
peekaboo image --analyze "這頁面在說什麼？"
```

## 注意事項
- 不消耗 LLM 額度
- 只有 --analyze 才會消耗

---

*更新：2026-02-24*
