# 系統備份

## 自動備份腳本
- **位置:** `~/.openclaw/backup/backup.sh`
- **排程:** 每天凌晨 3 點（待設定）
- **內容:**
  - `openclaw.json` - 全部設定
  - `.env` - API Keys
- **保留:** 7 天

## 恢復指令
```bash
cd ~/.openclaw/backup
tar -xzf openclaw_backup_2026-02-24_095507.tar.gz
cp openclaw.json.* ~/.openclaw/openclaw.json
```

## 狀態
- [x] 腳本已建立
- [x] 首次備份成功
- [ ] Cron 排程（待設定）

---
*2026-02-24 記錄*
