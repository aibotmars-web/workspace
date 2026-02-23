# 記憶分類索引

## 目的
將記憶拆分為主題分類，提升搜尋效率。

## 分類清單

| 分類檔案 | 說明 |
|----------|------|
| [agent-to-agent.md](./agent-to-agent.md) | Agent 與 Agent 之間的溝通協議與協作邏輯 |
| [multi-agent.md](./multi-agent.md) | 多代理協作系統的架構與任務分配技巧 |
| [browser-automation.md](./browser-automation.md) | 瀏覽器自動化操作實戰經驗 |
| [config-lessons.md](./config-lessons.md) | OpenClaw 配置教訓與最佳實踐 |
| [docker-sandbox.md](./docker-sandbox.md) | Docker 沙箱環境搭建與安全隔離 |
| [node-setup.md](./node-setup.md) | 伺服器節點配置、環境依賴安裝 |
| [model-management.md](./model-management.md) | 模型調用策略與思考級別設置 |
| [services-and-skills.md](./services-and-skills.md) | 自定義 Skill 開發與外部 API 調用 |
| [webhook-external.md](./webhook-external.md) | 外部服務 Webhook 集成 |
| [workflow-rules.md](./workflow-rules.md) | 自動化工作流核心規則與 SOP |
| [memory-lancedb-pro.md](./memory-lancedb-pro.md) | Markdown 升級到 LanceDB 向量資料庫 |

---

## 使用方式

搜尋時：
- 直接問問題，系統會自動搜尋相關分類
- 或指定分類：`搜尋 model-management 相關內容`

## 更新原則
- 每個分類獨立更新，不互相干擾
- 主索引檔保持輕量（2-3KB）
- 詳細內容寫入對應分類檔案

---

*建立時間：2026-02-23*
*參考來源：win4r YouTube 影片教學*
