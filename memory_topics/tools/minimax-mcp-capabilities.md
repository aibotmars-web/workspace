# MiniMax 內建 MCP 功能

## 來源
- 日期：2026-02-08
- 圖片來源：MiniMax 官方 MCP 使用指南

## 核心能力

### 1. 網路搜尋 (web_search)
- 功能：網頁搜尋
- 使用場景：查找資料、獲取最新資訊

### 2. 圖片理解 (understand_image)
- 功能：分析圖片內容
- 使用場景：理解截圖、設計稿、程式碼截圖

### 3. Coding Plan MCP
- 專屬於編碼場景
- 結合網路搜尋 + 圖片理解

## 重要提醒
- ✅ MiniMax 內建這些 MCP
- ✅ 無需 OpenAI API Key
- ✅ 所有 Sub-Agents 都應該知道這些能力

## 自動執行
- 收到圖片時 → 使用 understand_image
- 需要查詢時 → 使用 web_search
- 編碼問題 → 使用 Coding Plan MCP
