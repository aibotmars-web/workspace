# 匿名帳號與信箱設定指南
# Anonymous Account & Email Setup Guide

## 📋 建立匿名 GitHub 帳號

### 步驟 1：準備環境

```bash
# 建議使用 Tor Browser 下載並安裝
# 下載網址：https://www.torproject.org/download/
```

### 步驟 2：建立匿名郵件帳戶

#### 選項 A：ProtonMail（推薦）

```bash
# 1. 使用 Tor Browser 訪問
# 2. 選擇 Sign Up → Free Plan
# 3. 填寫資料：
#    - Username: [研究主題]_research_[隨機字串]
#    - Password: 強密碼（建議使用密碼管理器生成）
#    - Recovery Email: 可選（使用另一個匿名信箱）
```

#### 選項 B：SimpleLogin（郵件別名服務）

```bash
# SimpleLogin 可以讓你擁有多個郵件別名
# 適合用於註冊各種服務而不暴露真實信箱
```

### 步驟 3：註冊 GitHub 帳號

1. 訪問 https://github.com
2. 使用 Tor Browser 確保 IP 隱藏
3. 使用匿名郵件地址註冊
4. 帳號命名建議：
   ```
   real_media_study_tw
   real_info_research_2024
   real_factcheck_lab
   ```

### 步驟 4：強化帳號安全

#### 啟用兩步驟驗證（2FA）

```bash
# 不要使用手機簡訊驗證（可能被追蹤）
# 建議使用：
# - YubiKey（硬體金鑰）
# - TOTP App（如：Authy, Aegis, Raivo OTP）
```

#### 設定安全金鑰

```bash
# 在 GitHub 中：
# Settings → Password and authentication → SSH and GPG keys
# 新增 YubiKey 或其他 FIDO2 安全金鑰
```

---

## 🔐 匿名郵件服務比較

| 服務 | 免費額度 | 加密 | 所在地 | 評分 |
|------|---------|------|--------|------|
| ProtonMail | 500MB | 端到端 | 瑞士 | ⭐⭐⭐⭐⭐ |
| Tutanota | 1GB | 端到端 | 德國 | ⭐⭐⭐⭐⭐ |
| SimpleLogin | 無限別名 | 轉址 | 法國 | ⭐⭐⭐⭐ |
| AnonAddy | 50個別名 | 轉址 | 英國 | ⭐⭐⭐⭐ |

---

## 📱 推薦的 2FA 應用程式

### 行動裝置

| 應用程式 | 平台 | 特色 |
|---------|------|------|
| **Aegis** | Android | 開源、可加密備份 |
| **Raivo OTP** | iOS | 輕量、iCloud 同步 |
| **Authy** | 跨平台 | 雲端備份（隱私疑慮）|

### 硬體金鑰

| 金鑰 | 類型 | 價格 |
|------|------|------|
| YubiKey 5 NFC | USB/NFC | ~$50 |
| YubiKey 5C | USB-C | ~$60 |
| Nitrokey FIDO2 | USB-A | ~$40 |

---

## 🧅 使用 Tor Browser 的最佳實踐

### 下載 Tor Browser

```bash
# 官方下載頁面
https://www.torproject.org/download/

# 驗證下載完整性（可选）
# gpg --verify tor-browser-linux64-13.0.14.tar.xz.asc
```

### Tor Browser 設定

```javascript
// about:config 中的推薦設定
// 1. 安全性等級調整為「最安全」
// 2. 禁用 JavaScript（必要時允許特定網站）
// 3. 禁用 WebGL
// 4. 啟用 HTTPS-Only 模式
```

### 避免的錯誤

```bash
# ❌ 不要在 Tor 中登入個人帳號
# ❌ 不要使用真實姓名或電話
# ❌ 不要分享可能被識別的資訊
# ❌ 不要下載執行不明檔案

# ✅ 使用虛擬鍵盤輸入密碼
# ✅ 定期清除瀏覽資料
# ✅ 單一用途後重啟瀏覽器
```

---

## 🔒 VPN 與代理設定

### 推薦的隱私 VPN（按讚數排序）

| VPN | 總部 | 無日誌政策 | 接受加密貨幣 |
|-----|------|-----------|-------------|
| Mullvad | 瑞典 | ✅ | ✅ |
| IVPN | 直布羅陀 | ✅ | ✅ |
| ProtonVPN | 瑞士 | ✅ | ✅ |

### 設定範例（Mullvad）

```bash
# 1. 使用 Tor 下載 Mullvad Client
# 2. 生成隨機帳號號碼
# 3. 連接到 WireGuard 或 OpenVPN
# 4. 啟用 Kill Switch
```

---

## 📝 匿名化檢查清單

建立新帳號前，請檢查：

- [ ] 使用 Tor Browser 或 VPN
- [ ] 使用匿名郵件地址
- [ ] 不使用真實姓名
- [ ] 不使用個人照片
- [ ] 不使用可能被識別的使用者名稱
- [ ] 不提及地理位置
- [ ] 不提及工作單位或學校
- [ ] 不使用相同的使用者名稱（跨平台）
- [ ] 啟用 2FA（使用 TOTP 或硬體金鑰）
- [ ] 使用強密碼（20+ 字元）
- [ ] 考慮使用筆名或代號

---

## ⚠️ 常見錯誤

### 1. 指紋追蹤

```javascript
// 瀏覽器指紋可能洩露身份
// 避免：
// - 自訂瀏覽器設定
// - 安裝過多擴展套件
// - 使用特殊的布景主題
```

### 2. 內容關聯

```markdown
# 如果你在多個地方使用相同風格寫作
# 可能被識別為同一人

# 解決方案：
# - 使用不同的寫作風格
# - 使用翻譯工具改寫
# - 使用 AI 協助匿名化
```

### 3. 時間分析

```bash
# 發佈時間可能洩露時區
# 解決方案：
# - 設定隨機發佈時間
# - 使用 UTC 時間
# - 避免在特定時間上線
```

---

## 🔄 定期維護

### 每週任務

```bash
# 1. 檢查帳號登入活動
# 2. 確認沒有異常存取
# 3. 更新密碼（可選）
```

### 每月任務

```bash
# 1. 檢查 2FA 備份碼
# 2. 清理不需要的 Repository
# 3. 更新軟體版本
```

### 每季任務

```bash
# 1. 評估隱私設定
# 2. 更換郵件別名
# 3. 檢查是否有資料外洩
# 4. 考慮更換 VPN 伺服器
```

---

## 📞 緊急情況處理

### 如果懷疑帳號被入侵

```bash
# 1. 立即變更密碼
# 2. 審查最近的登入活動
# 3. 檢查已授權的應用程式
# 4. 考慮廢棄該帳號
```

### 如果身份可能暴露

```bash
# 1. 停止使用該帳號
# 2. 清除所有關聯內容
# 3. 建立新的匿名帳號
# 4. 提高未來的安全措施
```

---

## 📚 參考資源

### 閱讀清單

- [Tor Project 文件](https://tb-manual.torproject.org/)
- [ProtonMail 安全指南](https://protonmail.com/security-guidelines)
- [GitHub 帳號安全](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)
- [EFF 隱私指南](https://ssd.eff.org/)

### 工具清單

| 用途 | 工具 |
|------|------|
| 瀏覽器 | Tor Browser |
| 密碼管理 | Bitwarden, KeePassXC |
| 2FA | Aegis, YubiKey |
| VPN | Mullvad, IVPN |
| 郵件 | ProtonMail, Tutanota |
| 郵件別名 | SimpleLogin, AnonAddy |
