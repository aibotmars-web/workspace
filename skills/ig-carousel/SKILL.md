---
name: ig-carousel
description: >
  IG Carousel 自動發文系統。抓取 RSS 新聞 → AI 改寫繁體中文 → 去 AI 味 → Hook 優化
  → 生成 10 張 1080x1080 圖片 → AI 封面（fal-ai FLUX）→ 品質檢查 → 發布到 Instagram。
  支援 crypto/finance/startup 三個頻道。
  當使用者提到「發 IG」「IG 發文」「Carousel」「圖卡」「Instagram 貼文」時觸發。
metadata:
  openclaw:
    emoji: "📸"
    requires:
      bins: ["python3"]
      env: ["FAL_KEY"]
    optional_env: ["PEXELS_API_KEY", "ANTHROPIC_API_KEY"]
---

# IG Carousel 自動發文系統

一鍵完成：抓新聞 → AI 改寫 → 去 AI 味 → Hook 優化 → AI 封面 → 10 張圖卡 → IG 發文

---

## 指令一覽

```bash
ig-carousel draft <channel>             # 生成草稿 + 3 張 AI 封面候選
ig-carousel select-cover <channel> <N>  # 套用第 N 張封面候選（1-3）
ig-carousel publish <channel>           # 發布上次草稿
ig-carousel post <channel>              # 完整發文（不經封面選擇，直接發）
ig-carousel preview <channel>           # 預覽最新草稿
ig-carousel history                     # 查看發文歷史
```

**channel**：`crypto`（預設）、`finance`、`startup`

---

## 9 步完整發文流程（推薦）

### Step 1：Pipeline 生成初稿 + 3 張封面候選

```bash
ig-carousel draft <channel>
```

Pipeline 內部流程：
1. RSS 抓取多個來源（依頻道不同，見下方 RSS 來源表）
2. 文章評分篩選最熱新聞（含 Twitter 熱度補充搜尋）
3. 去重檢查（`posted_history.json`）
4. MiniMax AI 改寫繁體中文文案（拆 Part1 + Part2，各 800+ 字避免截斷）
5. 生成 10 張 1080x1080 Carousel 圖片
6. AI 封面生成（fal-ai FLUX schnell，見下方 AI 封面系統）
7. 品質閘門檢查（中文比例 ≥50%、圖片亮度正常）
8. 生成 3 張 AI 封面候選（`cover_candidate_1/2/3.jpg`，不同 seed）
9. 儲存草稿到 `cards/<channel>_<timestamp>/`

### Step 2：讀取文案

```bash
# 找最新 cards 目錄
LATEST=$(ls -td ~/.openclaw/workspace/agents/assistant-work/cards/<channel>_* 2>/dev/null | head -1)
# 讀取文案
read("$LATEST/caption.txt")
```

### Step 3：封面候選檢查

用 `understand_image` 看 3 張封面候選 + 佐證頁：

```
understand_image("$LATEST/cover_candidate_1.jpg")   # 封面候選 1
understand_image("$LATEST/cover_candidate_2.jpg")   # 封面候選 2
understand_image("$LATEST/cover_candidate_3.jpg")   # 封面候選 3
understand_image("$LATEST/<channel>_*_s03.jpg")     # 佐證頁（Slide 3）
```

**封面候選評估重點：**
- ✅ 跟新聞主題相關？（暴跌 → 紅色衝擊感、利好 → 金色喜氣）
- ✅ 構圖清晰不雜亂？
- ✅ 藝術風格正確？（見下方情緒→風格對應表）
- ❌ 跟主題不搭 → 記錄問題

**佐證（Slide 3）檢查：**
- 走勢圖模式 → 圖表標題、價格、漲跌幅清晰嗎？
- 照片模式 → 照片跟配文一致嗎？

### Step 4：通知老闆選封面

```
sessions_send(-5107483605, "📸 封面候選已生成，請選 1/2/3：")
# 附上 3 張圖的檔案路徑讓老闆看
```

等老闆回覆選哪張（如果老闆沒回，預設用你覺得最好的那張）。

### Step 5：套用選中的封面

```bash
ig-carousel select-cover <channel> <N>
```

N = 老闆選的那張（1-3）。這會用候選圖替換 Slide 1。

### Step 6：Humanizer 去 AI 痕跡

掃描文案，找出並改寫以下 AI 寫作模式：

| 模式 | 問題範例 | 改寫方向 |
|------|---------|---------|
| 意義膨脹 | 「標誌著XX的關鍵轉折」 | 直接講事實 |
| AI 詞彙 | 「深入探討」「至關重要」「全面性」 | 口語「來聊聊」「很重要」 |
| 模糊引用 | 「專家認為」「業界表示」 | 具名「分析師 xxx 說」 |
| 三連排比 | 「創新、突破、顛覆」 | 減少排比，用具體描述 |
| emoji 過多 | 🚀💡✅🔥 塞滿全文 | 一段最多 1-2 個 |
| 萬用結尾 | 「未來值得期待」「讓我們拭目以待」 | 給具體預測或行動建議 |
| 句長均勻 | 每句都 20-30 字 | 要有長有短（burstiness） |

**改寫風格**：台灣 PTT/Dcard 鄉民口語。可以用「靠北」「扯爆」「直接噴」。
數據要精確：不說「大幅成長」，說「漲了 12%」。

改好後覆蓋 caption.txt：
```
write("$LATEST/caption.txt", "改寫後的文案")
```

### Step 7：Hook 標題優化

檢查 caption.txt 第一行是否夠吸引人，套用高留存公式：

| 公式 | 模板 | 範例 |
|------|------|------|
| 數字衝擊 | `{數字}+{動詞}+{結果}` | 「3 天蒸發 200 億！機構跑了」 |
| 問句懸念 | `{話題}要{結果}？{懸念}` | 「比特幣要崩了？看完再說」 |
| 反常識 | `所有人都{行為}，但{反轉}` | 「大家都在追高，我勸你等等」 |
| 時效緊急 | `剛剛！{事件}` | 「剛剛！SEC 突然宣布新規」 |
| 爭議引戰 | `{主體}這操作，{評價}` | 「這波操作，散戶直接被割」 |

如果改了 Hook，同步更新 caption.txt。

### Step 8：發布

```bash
ig-carousel publish <channel>
```

⚠️ 用 publish 發布 draft 的圖片 + 改好的文案。**不要**再跑一次完整 pipeline。

### Step 9：記錄

用 `memory_store` 記錄：
- 發文標題
- understand_image 發現的問題
- humanizer 改了哪些
- 成功/失敗

---

## AI 封面系統

### 技術架構

- **模型**：fal-ai FLUX schnell（~$0.003/張）
- **端點**：`https://fal.run/fal-ai/flux/schnell`（同步 API，非 queue）
- **圖片規格**：1080x1080 square_hd，4 inference steps
- **3 候選機制**：每張用不同 seed（`time_ms + idx * 137`）產生變化

### 情緒偵測 → 藝術風格對應

Pipeline 自動偵測文章情緒（`_detect_article_mood()`），對應不同藝術風格：

| 情緒 | 觸發關鍵字 | 藝術風格 | 色調 |
|------|-----------|---------|------|
| crash | 暴跌、崩盤、crash、plunge、dump | Marvel 漫畫風 | 紅色/橙色衝擊 |
| bullish | 新高、牛市、bull、surge、rally | Andy Warhol 普普風 | 金色/藍色活力 |
| regulation | 監管、SEC、ban、法規、regulation | 賽博龐克風 | 紫色/霓虹冷調 |
| etf | ETF、基金、fund、spot | Andy Warhol 普普風 | 金色/海軍藍 |
| hack | 駭客、hack、stolen、漏洞、exploit | 賽博龐克風 | 綠色/矩陣霓虹 |
| default | （無特殊關鍵字） | Andy Warhol 普普風 | 標準配色 |

### 人物文章處理

當文章提到特定人物（川普、馬斯克等），`_build_person_prompt()` 生成含人物的藝術風格 prompt：

```
"{style} of {person}, {scene}, square format"
```

例如：crash 情緒 + 川普 → 「Marvel comic book style dramatic illustration of Trump, at a tense press conference with red financial charts crashing behind...」

### 封面生成優先順序

1. **AI 封面**（fal-ai FLUX schnell）— 最高優先
2. **OG Image**（文章原始圖片）
3. **Pexels 搜圖**（需 PEXELS_API_KEY）
4. **程式化背景**（Pillow 演算法藝術）— 最終 fallback

---

## 智慧資產偵測與走勢圖

### 加密貨幣偵測表（`_COIN_MAP`，CoinGecko API）

| 關鍵字 | CoinGecko ID | 圖表標籤 |
|--------|-------------|---------|
| btc / 比特幣 / bitcoin | bitcoin | BTC |
| eth / 以太 / ethereum | ethereum | ETH |
| sol / solana | solana | SOL |
| bnb | binancecoin | BNB |
| xrp / ripple | ripple | XRP |
| doge / 狗狗幣 / dogecoin | dogecoin | DOGE |
| ada / cardano | cardano | ADA |
| dot / polkadot | polkadot | DOT |
| avax / avalanche | avalanche-2 | AVAX |
| matic / polygon | matic-network | MATIC |
| link / chainlink | chainlink | LINK |
| sui | sui | SUI |
| ton | the-open-network | TON |

### 商品/貴金屬偵測表（`_COMMODITY_MAP`，Yahoo Finance API）

| 關鍵字 | Yahoo Symbol | 圖表標籤 |
|--------|-------------|---------|
| 黃金 / gold | GC=F | 黃金 |
| 白銀 / silver | SI=F | 白銀 |
| 原油 / oil / wti | CL=F | 原油 |
| 布蘭特 / brent | BZ=F | 布蘭特原油 |
| 銅 / copper | HG=F | 銅 |
| 天然氣 / natural gas | NG=F | 天然氣 |

### 圖表邏輯

- **只在偵測到特定資產時才顯示走勢圖**（不會每篇都放）
- **加密貨幣優先**：若同時偵測到幣種和商品，優先顯示幣種
- **只在 crypto/finance 頻道生效**
- 加密貨幣數據來源：CoinGecko API（免費）
- 商品數據來源：Yahoo Finance API（免費）
- 暴跌文章自動切換為 24 小時走勢（關鍵字：暴跌、崩盤、crash、dump 等）
- 預設顯示 7 天走勢

### 純 Pillow 極簡圖表

- **無 matplotlib 依賴**，純 Pillow 繪製
- CoinMarketCap app 風格：漸層面積圖 + 折線
- 高點/低點標記帶光暈效果
- 顯示資產名稱、當前價格、漲跌幅
- 漲 → 綠色漸層、跌 → 紅色漸層

---

## RSS 來源

### crypto 頻道（8 個來源）

| 來源 | 語言 | 說明 |
|------|------|------|
| 動區動趨 | 中文 | 台灣最大加密貨幣媒體 |
| 金色財經 | 中文 | 中國加密貨幣媒體 |
| 幣學 | 中文 | 台灣加密貨幣教育媒體 |
| Bitcoin Magazine | 英文 | BTC 專題深度報導 |
| Decrypt | 英文 | Web3 + 加密新聞 |
| The Block | 英文 | 機構級加密研究 |
| CoinTelegraph | 英文 | 全球最大加密媒體 |
| CoinDesk | 英文 | 加密產業標準媒體 |

### finance 頻道（7 個來源）

| 來源 | 語言 | 說明 |
|------|------|------|
| 經濟日報 | 中文 | 台灣財經主流媒體 |
| TechNews 財經 | 中文 | 科技財經交叉報導 |
| Yahoo 財經 | 中文 | 台灣散戶常用 |
| Google 財經 | 中文 | 自動聚合繁中熱門財經（涵蓋川普、戰爭、黃金等） |
| MarketWatch | 英文 | 道瓊旗下財經媒體 |
| CNBC Top News | 英文 | 美國主流財經電視 |
| Bloomberg Markets | 英文 | 全球金融市場 |

### startup 頻道（4 個來源）

| 來源 | 語言 | 說明 |
|------|------|------|
| Inside | 中文 | 台灣科技創業媒體 |
| TechNews 台灣 | 中文 | 台灣科技新聞 |
| TechCrunch | 英文 | 矽谷創業標杆媒體 |
| Crunchbase News | 英文 | 融資與創業數據 |

---

## 文章評分熱門關鍵字

### crypto

BTC、比特幣、ETH、SOL、XRP、BNB、ETF、川普、馬斯克、SEC、穩定幣、儲備、牛市、新高、coinbase、binance、AI、BlackRock

### finance

美股、台股、納斯達克、道瓊、聯準會、Fed、升息、降息、通膨、CPI、川普、關稅、戰爭、中美、台海、烏克蘭、以色列、黃金、白銀、原油、AI、輝達、NVIDIA、蘋果、特斯拉、巴菲特、GDP、就業率、IPO

### startup

AI、OpenAI、ChatGPT、融資、估值、獨角獸、IPO、裁員、併購、創辦人、台灣、矽谷、Anthropic、Google、Apple、Meta

---

## 頻道與帳號

| 頻道 | IG 帳號 | 說明 |
|------|---------|------|
| crypto | @money.showtime | 加密貨幣新聞 |
| finance | @money.showtime | 金融市場新聞（川普、戰爭、黃金白銀、世界趨勢） |
| startup | @bossmaker.lab | 創業故事 |

---

## 排程

- `auto-post-crypto`：每天 09:01 自動執行 `ig-carousel draft crypto` → 完整 9 步流程

---

## 環境變數

| 變數 | 必要性 | 說明 |
|------|--------|------|
| `FAL_KEY` | **必要** | fal-ai API key（AI 封面生成） |
| `PEXELS_API_KEY` | 選用 | Pexels 圖庫搜圖（封面 fallback） |
| `ANTHROPIC_API_KEY` | 選用 | Claude API（未來擴充用） |

FAL_KEY 已內建在 `ig-carousel.sh` 中，通過 skill 執行時自動載入。

---

## 輸出檔案結構

每次 draft 生成在 `~/.openclaw/workspace/agents/assistant-work/cards/<channel>_<timestamp>/`：

```
<channel>_<timestamp>/
├── <channel>_<timestamp>_s01.jpg    # Slide 1（封面/Hook）
├── <channel>_<timestamp>_s02.jpg    # Slide 2（摘要）
├── <channel>_<timestamp>_s03.jpg    # Slide 3（佐證/走勢圖）
├── ...
├── <channel>_<timestamp>_s10.jpg    # Slide 10（CTA）
├── cover_candidate_1.jpg            # AI 封面候選 1
├── cover_candidate_2.jpg            # AI 封面候選 2
├── cover_candidate_3.jpg            # AI 封面候選 3
├── caption.txt                      # Instagram 文案
└── article_meta.json                # 文章元資料（URL、標題、hook、來源）
```

---

## 檔案位置

| 檔案 | 路徑 |
|------|------|
| Pipeline 主控 | `~/.openclaw/workspace/scripts/social-media/content_pipeline.py` |
| 圖片生成 | `~/.openclaw/workspace/scripts/social-media/make_card.py` |
| IG 發文 | `~/.openclaw/workspace/scripts/social-media/ig_post.py` |
| Skill 腳本 | `~/.openclaw/workspace/skills/ig-carousel/scripts/ig-carousel.sh` |
| 輸出目錄 | `~/.openclaw/workspace/agents/assistant-work/cards/` |
| 去重記錄 | `~/.openclaw/workspace/scripts/social-media/posted_history.json` |
| IG 設定 | `~/.openclaw/workspace/scripts/social-media/ig_config.json` |
| Startup IG 設定 | `~/.openclaw/workspace/scripts/social-media/startup_ig_config.json` |

---

## 常見問題

| 問題 | 解法 |
|------|------|
| Pipeline 全失敗 | 檢查 MiniMax 是否正常回應，看 stderr 輸出 |
| AI 封面沒生成 | 確認 `FAL_KEY` 環境變數有設定（ig-carousel.sh 已內建） |
| 封面候選都太像 | 正常現象，每張用不同 seed 但 prompt 相同 |
| 文案太淺 | 確認 Part1+Part2 各 800+ 字，MiniMax 沒截斷 |
| 重複發文 | 檢查 `posted_history.json`，pipeline 自動跳過已發文章 |
| IG 登入失敗 | 檢查 `ig_config.json` 的 session 是否過期 |
| 走勢圖沒出現 | 只在偵測到特定幣種關鍵字時才顯示（非每篇都有） |
| JSON 解析失敗 | MiniMax stdout 可能混入 `[plugins]` 前綴，程式已自動處理 |
| 每篇都放 BTC 圖 | 已修復：只在文章提到特定幣種時才顯示對應走勢圖 |

---

## ⚠️ 重要注意事項

1. **所有 IG 發文都用 `ig-carousel` skill 指令**，不要直接跑 `python3 content_pipeline.py`
2. **發布前一定要先 draft**，不要直接 `post`（除非排程自動執行）
3. **封面很重要**：好封面 = 高點擊率，一定要用 `understand_image` 檢查
4. **Humanizer 是必要步驟**：AI 原始文案一定有 AI 味，必須改寫
5. **publish 只發布上次 draft 的結果**，不會重新抓新聞或生成圖片
