# GitHub Pages 部署指南
# GitHub Pages Deployment Guide

## 📋 目錄

1. [概覽](#概覽)
2. [方法一：從 main 分支部署](#方法一從-main-分支部署)
3. [方法二：從 gh-pages 分支部署](#方法二從-gh-pages-分支部署)
4. [使用 Actions 自動部署](#使用-actions-自動部署)
5. [常見問題](#常見問題)
6. [故障排除](#故障排除)

---

## 概覽

### 什麼是 GitHub Pages？

GitHub Pages 是 GitHub 提供的靜態網站託管服務，適合：
- 專案文件
- 個人網站
- 靜態部落格
- 研究報告展示

### 價格

✅ **完全免費**（公開 Repository）

### 限制

- 軟體限制：1GB
- 月流量：100GB
- 每小時建構次數：10 次

---

## 方法一：從 main 分支部署

### 適用場景

靜態 HTML 檔案直接放在 Repository 根目錄

### 步驟

```bash
# 1. 建立 Repository（如果是新專案）
#    Repository 名稱：[你的帳號名].github.io

# 2. Clone 到本機
git clone https://github.com/[帳號名]/[repo名稱].git
cd [repo名稱]

# 3. 將 index.html 放入根目錄
#    結構範例：
#    ├── index.html
#    ├── about.html
#    ├── css/
#    │   └── style.css
#    └── js/
#        └── script.js

# 4. 提交並推送
git add .
git commit -m "Initial commit"
git push origin main

# 5. 前往 https://[帳號名].github.io 查看網站
```

### 啟用 Pages

```bash
# 1. 進入 Repository → Settings
# 2. 點擊左側 Pages
# 3. Source 選擇 "Deploy from a branch"
# 4. Branch 選擇 "main" / "(root)"
# 5. 點擊 Save
```

---

## 方法二：從 gh-pages 分支部署

### 適用場景

需要將編譯後的輸出放在獨立分支，保持原始碼整潔

### 步驟

```bash
# 1. 建立 gh-pages 分支（空的）
git checkout --orphan gh-pages

# 2. 移除所有檔案（保留必要的靜態檔案）
git rm -rf .

# 3. 加入你的靜態檔案
cp -r ../dist/* .
# 或者：從 public/ 或 build/ 目錄複製

# 4. 提交
git add .
git commit -m "Deploy to GitHub Pages"

# 5. 推送
git push origin gh-pages

# 6. 在 Settings → Pages 中選擇 gh-pages 分支
```

### 自動化脚本

```bash
#!/bin/bash
# deploy.sh - 自動部署脚本

echo "🚀 開始部署..."

# 建構專案
npm run build

# 切換到 gh-pages
git checkout gh-pages

# 清除舊檔案
git rm -rf .

# 複製新檔案
cp -r ../dist/* .

# 提交
git add .
git commit -m "Deploy: $(date)"

# 推送
git push origin gh-pages

# 回到 main
git checkout main

echo "✅ 部署完成！"
```

---

## 方法三：使用 Actions 自動部署（推薦）

### Workflow 設定

本專案已包含 `.github/workflows/deploy.yml`

### 步驟

```bash
# 1. 確保 workflow 檔案在正確位置
#    .github/workflows/deploy.yml

# 2. Push 到 main 分支
git add .
git commit -m "Add deploy workflow"
git push origin main

# 3. 查看部署狀態
#    Repository → Actions 頁面
```

### 設定 Pages 權限

```yaml
# deploy.yml 中的關鍵設定
permissions:
  contents: read
  pages: write
  id-token: write
```

### 等待部署

```bash
# 1. GitHub Actions 會自動執行
# 2. 部署完成後會顯示綠色勾勾
# 3. 前往 Settings → Pages 查看連結
```

---

## 常見問題

### Q1：網站沒有更新？

```bash
# 1. 檢查 Actions 是否執行成功
#    Repository → Actions

# 2. 清除瀏覽器快取
#    Ctrl + F5 (Windows/Linux)
#    Cmd + Shift + R (Mac)

# 3. 檢查部署紀錄
#    Settings → Pages → 查看 Deployment history
```

### Q2：CSS/JS 沒有載入？

```bash
# 檢查路徑設定

# ❌ 錯誤：絕對路徑
<link rel="stylesheet" href="/css/style.css">

# ✅ 正確：相對路徑
<link rel="stylesheet" href="css/style.css">

# ✅ 正確：使用 base URL
<base href="${{ site.baseurl }}/">
```

### Q3：自訂網域問題？

```bash
# 1. 在 Settings → Pages 中輸入網域
# 2. 建立 CNAME 檔案（可選）

# DNS 設定
# ├── @ → CNAME → [你的帳號名].github.io
# ├── www → CNAME → [你的帳號名].github.io
```

### Q4：HTTPS 問題？

```bash
# GitHub Pages 自動提供 SSL 憑證
# 如果使用自訂網域：
# 1. 等待 DNS 傳播（最多 24 小時）
# 2. 在 Settings → Pages 中啟用"Enforce HTTPS"
```

### Q5：404 錯誤？

```bash
# 常見原因：
# 1. 檔案不在正確位置
# 2. 副檔名問題（.html vs 沒有）
# 3. 大小寫敏感（Linux 伺服器）

# 解決方案：
# 1. 確認 index.html 在根目錄
# 2. 使用正確的副檔名
# 3. 檢查檔案大小寫
```

---

## 故障排除

### 檢查清單

- [ ] Repository 是公開的（Public）
- [ ] Source 分支設定正確
- [ ] 檔案在正確的目錄
- [ ] Actions 執行成功
- [ ] 瀏覽器快取已清除

### 查看建構日誌

```bash
# 在 Actions 頁面中：
# 1. 點擊失敗的工作流
# 2. 查看每個步驟的輸出
# 3. 找到錯誤訊息
```

### 常見錯誤訊息

| 錯誤 | 解決方案 |
|------|----------|
| `No source branch found` | 在 Settings 中選擇正確分支 |
| `Build timeout` | 減少建構時間，最佳化流程 |
| `File too large` | 壓縮圖片，減少資源大小 |
| `Permission denied` | 檢查 workflow 權限設定 |

---

## 進階設定

### 使用自訂網域

```yaml
# 在 deploy.yml 中
- name: Deploy
  uses: actions/deploy-pages@v4
  with:
    domain: example.your-domain.com
    enable_auto_https: true
```

### 部署預覽

```yaml
# 為每個 PR 建立預覽
name: Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: npm run build
      - name: Upload preview
        uses: actions/upload-artifact@v4
        with:
          name: preview
          path: build
```

### 環境保護

```yaml
# 設定部署審查
environment:
  name: github-pages
  url: ${{ steps.deployment.outputs.page_url }}
```

---

## 效能優化

### 減少建構時間

```bash
# 1. 快取依賴套件
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 壓縮圖片

```bash
# 使用 imagemin 或 squoosh
npm install --save-dev imagemin
```

### 啟用 Gzip/Brotli

```bash
# GitHub Pages 自動啟用壓縮
# 無需額外設定
```

---

## 參考連結

| 主題 | 連結 |
|------|------|
| GitHub Pages 文件 | https://docs.github.com/en/pages |
| 自訂網域 | https://docs.github.com/en/pages/configuring-a-custom-domain |
| Actions 部署 | https://docs.github.com/en/actions/deploying/deploying-with-github-actions |
| 疑難排解 | https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-404-errors |
