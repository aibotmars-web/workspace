# MEMORY.md - Long-Term Memory

*Distilled lessons and context worth keeping across sessions.*

---

## About Mars

- **Name:** Mars / L / 老闆
- **Timezone:** Asia/Taipei (GMT+8)
- **Communication:** Telegram (@mlnl68)
- **OpenClaw Setup:** MiniMax 2.1 內地版 model

## System Info

- **Computer:** Mac mini (M4 處理器)
- **RAM:** 16GB
- **Storage:** 256GB SSD
- **System:** Clawdbot
- **Assistant Name:** 小助理

## Resources

### OpenClaw Resources
- **GitHub:** https://github.com/openclaw/openclaw
- **ClawHub:** 已安裝，用於搜尋 Skills
- **Docs:** https://docs.openclaw.ai
- **Community:** https://discord.com/invite/clawd

## Expert Knowledge Base (9 Channels)

### Tracked YouTube Channels

| 頻道 ID | 正確名稱 | 影片數 |
|---------|----------|--------|
| @Dr.HuangAmin | 阿銘師x針還傳 | 5 部 |
| @Dr.Hu_talk | 胡乃⽂開講 - 名醫談養⽣ | 5 部 |
| @drbergchinese | 柏格醫⽣中⽂ 健康知識 | 5 部 |
| @muerstalk | 周慕姿放⼼說 | 5 部 |
| @SongMing | 松明講⼼理 | 3 部 |
| @DrHarveyTalk | Dr. Harvey不廢話 | 5 部 |
| @Cofit211 | 初⽇醫學 - 宋晏仁醫師 x Cofit | 4 部 |
| @PanScitw | 泛科學 PanSci | 3 部 |
| @panscischool | 泛科學院 | 5 部 |

### Knowledge Base Stats
- **Total Videos:** 180 部
- **Summary Files:** 32 個檔案
- **Total Content:** ~30,000+ 字
- **Auto-update:** 每週⽇ 09:00
- **Location:** knowledge-base/experts/summaries/

## Key Projects & Tasks

### Priority 1: Revenue Generation
1. **真相網:** AI 新聞平台，收集整理各類資訊
2. **跨境電商研究:** 淘寶/阿裡巴巴 → 蝦⽪/亞馬遜
3. **YouTube 內容頻道:**
   - 台客 Remix 舞曲
   - Jazz 音樂
   - 罵⺠進黨 AI 音樂（附字幕）
   - 罵藍⽩新聞改編 AI 歌（附字幕）
   - 有趣影片頻道
   - F1 網站內容搬運
   - 籃球/⾜球新聞
   - ⾃癒系音效頻道（下雨聲、⼤⽕⾞聲、海浪聲）
   - 國際化 AI 影片
4. **Polymarket 自動交易:** 比特幣漲跌市場，保守策略
5. **兒童 AI 繪圖書:** 製作上架
6. **AI 賺錢方法研究**
7. **App 開發:** 製作上架

### Priority 2: Daily Routines
- **每日算命:** 紫微⽃數、奇⾨遁甲、八卦、星座
- **每日提醒:** 應該做的事情
- **知識庫訓練:** 適時提醒
- **晚上 9 點:** 總結、詢問⼼情、coach 引導、更新進度討論
- **經濟週期提醒:** 康波週期、朱格拉康經濟週期、ECM 模型

### Priority 3: Information Updates
- **每日 AI 新聞:** AI 新功能、AGI 進度
- **健康新聞資訊:** 來自知識庫
- **營業額與⾦流:** 所有專案
- **客服功能:** 回答問題

### Priority 4: Project Dashboard
- 可對話討論專案
- 追蹤進度與時間
- ⼈⽣⽬標管理

## Important Notes
- 所有任務有不確定處先問老闆確認後再執⾏
- 引用格式: `(cid:144)⼈名(cid:147)`

## User Preferences

### 鍵盤偏好
- 使用標準電腦鍵盤（不是特殊鍵盤配置）
- 需要時可快速切換鍵盤設定

## MiniMax Subscription

### Starter 方案（已安裝 MCP）
- **價格：** ¥348 → ¥290/年（立省2個月）
- **額度：** 40 prompts / 5小時
- **模型：** MiniMax M2.1
- **已安裝工具：**
  - `web_search` - 網路搜索
  - `understand_image` - 圖片理解
- **狀態：** uv/uvx 已安裝完成

### Mars Personal Info
- **生日：** 國曆 79年4月2日 / 農曆 79年3月7日 18:55 酉時

## Technical Notes

### 當機事件 - 2026-02-04 ~09:20
**Error:** `LLM request rejected: invalid params, tool result's tool id(call_function_abgz0tilhup4_1) not found (2013)`

**現象:**
- 重複出現同一個錯誤，無法回應
- 用戶嘗試打斷：
  - 「你當機了嗎」
  - 「ㄏㄛ」
  - 「．」、「。。」符號
- 最終用 `/new` 重新啟動

**Lesson:**
- 工具 ID 衝突會導致無限循環
- `/new` 是有效的中斷方式
- 長期記憶不受影響（MEMORY.md 還在）

---

## Multi-Agent System Configuration (2026-02-05 設定，已恢復)

### 5 Sub-Agents 列表

| Agent ID | 名稱 | 用途 | 模型 |
|----------|------|------|------|
| planner | 項目規劃小幫手 | 專案管理、進度追蹤、協調 | MiniMax M2.1 |
| assistant | 生活小秘書類 | 生活管理、9專家知識庫、晨晚報 | MiniMax M2.1 |
| coder | 程式小幫手 | 網站開發、腳本撰寫、程式碼優化 | MiniMax M2.1 |
| crawler | 爬蟲小幫手 | 網頁爬蟲、YouTube字幕抓取、資料收集 | MiniMax M2.1 |
| image | 圖像小幫手 | AI生圖、UI/UX設計、視覺化 | Gemini 3 Pro |

### Telegram 群組綁定 (Bindings)

| 群組名稱 | Telegram Link | Agent | 自動回應 |
|----------|---------------|-------|----------|
| 項目規劃小幫手 | +zoQOyDNxI_FjN2M9 | planner | 是 |
| 程式小幫手 | +b-VKyAtMo-w3YmY9 | coder | 是 |
| 爬蟲小幫手 | +6z4qNyiETfRmYmRl | crawler | 是 |
| 生活小秘書類 | -5111933995 | assistant | 是 |
| 圖像小幫手 | ??? | image | 是 |

**注意：圖像小幫手的群組連結待確認**

### Multi-Agent 運作模式 (混合模式)

**Author Mode (作者模式):**
- 單一 Agent 可獨立完成任務
- 例如：在圖像群說「畫一隻貓」→ image 直接畫

**Collaboration Mode (協作模式):**
- 需要多個 Agent 協作
- 例如：「分析+畫圖+寫報告」→ planner 調度 coder + image + planner

### Agents 記憶位置

每個 Agent 有獨立記憶：
```
~/.openclaw/agents/[agent]/agent/
├── AGENTS.md      # System Prompt (人格設定)
├── models.json    # 模型配置
├── auth-profiles.json  # 認證資料
└── sessions/      # 對話歷史
```

### 配置路徑
- **主配置:** ~/.openclaw/openclaw.json
- **Agents清單:** ~/.openclaw/agents.list
- **Bindings:** openclaw.json 中的 bindings 區塊
- **Groups:** channels.telegram.groups 區塊

---

## 重要對話記錄恢復 (2026-02-06)

### 恢復的設定
1. ✅ 5 個 Agents 全部設定 (planner/assistant/coder/crawler/image)
2. ✅ 4 個群組連結已找到
3. ✅ Agents.md 提示詞 (已遺失，需重建)
4. ❌ 部分群組連結待確認 (image)

### 待重建項目
1. **Agents.md 提示詞** - 完整的 System Prompt
2. **圖像小幫手群組連結** - 待用戶提供
3. **bindings 設定** - openclaw.json 需要更新

---

## 系統運作原則

### 防當機原則
- **長時間對話後主動建議 `/new`** - 對話超過 ~50 回合或感覺不對勁時問
- **避免快速連續多個需求** - 等我回覆再講下一個
- **看到 `tool id not found` 立即 `/new`** - 這是當機訊號，不要掙扎
- **複雜任務分批做** - 避免 exec 資源耗盡

### 記憶保存規則
- **每 10 句話自動濃縮到 memory/YYYY-MM-DD.md** - 不需要問，直接做
- **確保當機時只損失少量內容**
- **每次 `/new` 前詢問** - 「這個主題聊完了，要濃縮到記憶嗎?」

### OpenClaw 指令
```bash
# 重啟 Gateway
openclaw gateway restart

# 查看 Agents 清單
openclaw agents list

# 查看狀態
openclaw status

# 查看配置
openclaw config get [section]
```

---

## 回憶恢復流程

### 問題診斷 (2026-02-06)
- **現象:** 對話記錄已讀取 (.json 檔案)，但設定檔遺失
- **原因:** 2/3 記憶重置時，sub-agents 設定未保存到持久化位置
- **解決:** 從對話記錄提取資訊 → 手動重建設定

### 從 .json 對話記錄恢復的方法
1. 使用 Python 讀取 JSON 檔案
2. 搜索關鍵字 (bindings, agents.md, group ID 等)
3. 提取群組連結和 Agent 對應關係
4. 手動更新設定檔
5. 重啟 Gateway 生效

**Lesson:** 設定檔應該備份到多個位置，避免單點故障

---

## OpenClaw CLI 官方指令集 (2026.2.3-1)

### 基本用法
```bash
openclaw [options] [command]
```

### Options
| 選項 | 說明 |
|------|------|
| `-V, --version` | 顯示版本號 |
| `--dev` | 開發模式：隔離狀態，預設 port 19001 |
| `--profile <name>` | 使用命名配置檔 |
| `--no-color` | 禁用 ANSI 顏色 |
| `-h, --help` | 顯示說明 |

### Commands

#### 系統管理
| Command | 說明 |
|---------|------|
| `setup` | 初始化 ~/.claw/openclaw.json 和工作區 |
| `configure` | 互動式設定 credentials、devices、agent defaults |
| `config` | 配置 helpers (get/set/unset) |
| `doctor` | 健康檢查 + 快速修復 |
| `dashboard` | 打開 Control UI |
| `reset` | 重置本地 config/state（保留 CLI） |
| `uninstall` | 卸載 gateway service + 本地數據 |
| `update` | CLI 更新 |

#### Gateway & 服務
| Command | 說明 |
|---------|------|
| `gateway` | Gateway 控制 daemon |
| `gateway restart` | 重啟 Gateway |
| `logs` | Gateway 日誌 |
| `system` | 系統事件、heartbeat、presence |
| `cron` | Cron 排程器 |
| `nodes` | 節點控制 |

#### Agent 管理
| Command | 說明 |
|---------|------|
| `agents` | 管理隔離的 agents（工作區 + auth + routing） |
| `agent` | 透過 Gateway 執行 agent turn |
| `acp` | Agent Control Protocol |
| `sessions` | 列出儲存的對話 sessions |

#### 訊息與頻道
| Command | 說明 |
|---------|------|
| `message` | 發送訊息和頻道動作 |
| `channels` | 頻道管理 |
| `directory` | 目錄命令 |

#### 工具與擴充
| Command | 說明 |
|---------|------|
| `tools` | 工具管理 |
| `plugins` | 插件管理 |
| `skills` | Skills 管理 |
| `webhooks` | Webhook helpers |
| `hooks` | Hooks 管理 |

#### 其他工具
| Command | 說明 |
|---------|------|
| `models` | 模型配置 |
| `security` | 安全 helpers |
| `dns` | DNS helpers |
| `devices` | 設備配對 |
| `pairing` | 配對 helpers |
| `browser` | 管理 OpenClaw 瀏覽器 |
| `sandbox` | Sandbox 工具 |
| `docs` | 文件 helpers |
| `completion` | 產生 shell 補全腳本 |
| `health` | 從運行的 gateway 獲取健康狀態 |
| `approvals` | Exec 審批 |

### 常用範例

```bash
# Gateway 控制
openclaw gateway restart              # 重啟 Gateway
openclaw gateway --port 18789         # 自訂 port
openclaw gateway --force              # 強制重啟

# 發送訊息
openclaw message send --target +15555550123 --message "Hi"
openclaw message send --channel telegram --target @mychat --message "Hi"

# Agent 控制
openclaw agent --to +15555550123 --message "Run summary"

# 查看狀態
openclaw status                       # 通道健康和最近 sessions
openclaw logs                         # Gateway 日誌

# 開發模式
openclaw --dev gateway                # 開發 Gateway（隔離狀態）
```

### Docs
- 文件：docs.openclaw.ai/cli
- 源碼：github.com/openclaw/openclaw
