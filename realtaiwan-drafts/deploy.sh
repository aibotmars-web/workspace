#!/bin/bash
# 真相網完整部署腳本 - 由 Coder Agent 在 Mac Mini 上執行
# 日期: 2026-03-01
# 安全提醒: 僅使用 realtaiwan 帳號，不得混用其他身份

set -e

REPO_DIR="/tmp/realtaiwan-web"
SITE_DIR="$HOME/.openclaw/workspace/realtaiwan-drafts/site"
TOKEN="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"

echo "=== 真相網完整部署腳本 ==="
echo "日期: $(date '+%Y-%m-%d %H:%M:%S')"

# Step 1: Clone repo
echo ""
echo "[1/5] 克隆 realtaiwan-web repo..."
rm -rf "$REPO_DIR"
git clone "https://${TOKEN}@github.com/realtaiwan/realtaiwan-web.git" "$REPO_DIR"

# Step 2: 設定 Git 身份（安全隔離）
cd "$REPO_DIR"
git config user.name "realtaiwan"
git config user.email "realtaiwan@proton.me"
echo "[2/5] Git 身份設定完成（realtaiwan 身份）"

# Step 3: 部署完整網站
echo "[3/5] 部署完整網站框架..."

# 複製首頁、關係圖、關於頁
cp "$SITE_DIR/index.html" "$REPO_DIR/index.html"
cp "$SITE_DIR/network.html" "$REPO_DIR/network.html"
cp "$SITE_DIR/media.html" "$REPO_DIR/media.html"
cp "$SITE_DIR/about.html" "$REPO_DIR/about.html"

# 複製 CSS
mkdir -p "$REPO_DIR/assets"
cp "$SITE_DIR/assets/article.css" "$REPO_DIR/assets/article.css"

# 複製文章頁面
mkdir -p "$REPO_DIR/articles"
cp "$SITE_DIR/articles/"*.html "$REPO_DIR/articles/"

echo "  首頁: index.html"
echo "  關於: about.html"
echo "  CSS:  assets/article.css"
echo "  文章: $(ls "$SITE_DIR/articles/"*.html | wc -l) 篇 HTML"

# Step 4: 檢查
echo "[4/5] 檢查檔案結構..."
echo "---"
find "$REPO_DIR" -name "*.html" -o -name "*.css" | sort
echo "---"

# Step 5: 提交並推送
echo "[5/5] 提交並推送..."
git add -A
git commit -m "真相網 v2.0 - 完整網站框架重建 (2026-03-01)

網站架構：
- 首頁：暗色主題新聞列表，分類篩選
- 關於頁：網站使命與原則
- 文章頁：統一模板，相關文章推薦

新增 5 篇文章：
- 柯文哲京華城案一審宣判倒數
- 憲法法庭 5 人判決憲政危機
- 劉世芳外甥政治獻金風波
- 黃國昌遭列貪污被告
- 2026 九合一選舉前瞻"

git push origin main

echo ""
echo "=== 部署完成 ==="
echo "網址: https://realtaiwan.github.io/realtaiwan-web/"
echo ""
echo "請等 1-2 分鐘讓 GitHub Pages 建置完成後再確認"

# 清理
rm -rf "$REPO_DIR"
echo "暫存目錄已清理"
