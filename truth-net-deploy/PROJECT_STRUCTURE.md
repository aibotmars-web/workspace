# 真相網專案結構
# Truth Network Project Structure

```
truth-network-site/
│
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 自動部署設定
│
├── blog/                        # 部落格文章（可選）
│   ├── 2024-01-01-welcome.md
│   └── 2024-01-02-research.md
│
├── docs/                        # 主要研究文件
│   ├── introduction.md         # 專案介紹
│   ├── methodology.md          # 研究方法
│   ├── findings.md             # 研究發現
│   ├── conclusion.md           # 結論
│   └── resources.md            # 資源連結
│
├── src/
│   ├── components/             # React 元件
│   │   ├── HomepageFeatures/
│   │   │   └── index.js
│   │   └── HomepageHero/
│   │       └── index.js
│   ├── css/
│   │   └── custom.css          # 自訂樣式
│   └── pages/
│       ├── index.js            # 首頁
│       ├── about.md            # 關於頁面
│       └── contact.md          # 聯繫頁面（可選）
│
├── static/                      # 靜態資源
│   ├── img/                    # 圖片
│   │   ├── logo.svg
│   │   └── favicon.ico
│   └── files/                  # 可下載檔案
│       └── research-report.pdf
│
├── docusaurus.config.js         # Docusaurus 設定檔
├── package.json                 # NPM 依賴
├── sidebars.js                  # 側邊欄設定
├── README.md                    # 專案說明
└── gitignore                    # Git 忽略檔案
```

---

## 詳細說明

### `.github/workflows/deploy.yml`

**用途**：GitHub Actions 自動部署工作流

**功能**：
- 監控 main 分支的變更
- 自動建構靜態網站
- 部署到 GitHub Pages

### `docs/`

**用途**：存放主要研究文件

**建議的檔案結構**：

```
docs/
├── tutorial-basics/            # 基礎教學
│   ├── installation.md
│   └── configuration.md
│
├── tutorial-expert/            # 進階內容
│   ├── data-analysis.md
│   └── case-studies.md
│
├── research-2024/              # 2024 年研究
│   ├── media-literacy.md
│   ├── fact-checking.md
│   └── misinformation.md
│
└── index.md                     # 文件首頁
```

### `src/css/custom.css`

**用途**：自訂網站樣式

**範例內容**：

```css
/* 顏色變數 */
:root {
  --ifm-color-primary: #25c2a0;
  --ifm-color-primary-dark: #21af90;
  --ifm-color-primary-darker: #1fa588;
  --ifm-color-primary-light: #29d5b0;
  --ifm-font-family-base: 'Noto Sans TC', sans-serif;
}

/* 深色模式 */
[data-theme='dark'] {
  --ifm-color-primary: #00d4aa;
}

/* 首頁樣式 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 4rem 0;
}

/* 研究文章樣式 */
.markdown h2 {
  color: #1fa588;
  border-bottom: 2px solid #eee;
}

.markdown blockquote {
  background: #f5f5f5;
  border-left: 4px solid #1fa588;
  padding: 1rem;
  margin: 1.5rem 0;
}
```

---

## 快速開始

### 1. 安裝依賴

```bash
npm install
```

### 2. 本機開發

```bash
npm start
# 前往 http://localhost:3000
```

### 3. 建構生產版本

```bash
npm run build
# 輸出至 build/ 目錄
```

### 4. 部署到 GitHub Pages

```bash
npm run deploy
```

---

## Git 忽略設定 (.gitignore)

```
# 依賴
node_modules/

# 建構輸出
build/
.cache/
dist/

# IDE
.idea/
.vscode/
*.swp
*.swo

# 系統檔案
.DS_Store
Thumbs.db

# 環境變數
.env
.env.local
```

---

## 常用命令

| 命令 | 說明 |
|------|------|
| `npm start` | 啟動開發伺服器 |
| `npm run build` | 建構生產版本 |
| `npm run serve` | 預覽建構結果 |
| `npm run deploy` | 部署到 GitHub Pages |
| `npm run clear` | 清除快取 |
| `docusaurus swizzle` | 自訂主題 |

---

## 部署流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                    開發流程                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 本機開發        2. 提交變更       3. Push 到 GitHub     │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐       │
│  │ npm start  │ →  │ git commit │ →  │ git push   │       │
│  └────────────┘    └────────────┘    └────────────┘       │
│                                             │               │
│                                             ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              GitHub Actions 觸發                     │   │
│  │              .github/workflows/deploy.yml            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                             │               │
│                                             ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              建構與部署                              │   │
│  │              npm run build                          │   │
│  │              → gh-pages 分支                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                             │               │
│                                             ▼               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              網站上線                                │   │
│  │              https://xxx.github.io/repo/             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 維護建議

### 定期更新

```bash
# 每週檢查依賴更新
npm outdated

# 更新 Docusaurus
npm install @docusaurus/core@latest
```

### 備份策略

```bash
# 本機備份
git clone https://github.com/your-username/truth-network-site.git backup

# 或使用 GitHub 的 Archive 功能
# Repository → Settings → Export data → Archive
```
