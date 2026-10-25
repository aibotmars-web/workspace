# 2026-08-05 ~ 2026-08-12 知識庫爬蟲修復教訓（8 天血淚）

## 問題
知識庫自動爬蟲停了 14 天。原因是 `cron 06:00` 呼叫的是過期腳本 `crawl-daily.sh`（只 echo「已退役」就 exit 0）。

## 已自動完成（✅）
1. 清 BCD 重複（1314 檔、釋放 2.31 GB）
2. wrapper 時間預算 13 → 60 分鐘
3. 寫 LaunchAgent `com.openclaw.kb-crawl.plist`（macOS 原生排程取代 cron）
4. 重命名壞腳本 `crawl-daily.sh` → `.disabled-20260809`
5. 驗證跑成功（知識庫 2979 → 3028）
6. 8/12 再清 25 個 .m4a（1.4GB → 332MB）

## 環境限制（❌ 砍不掉）
- `crontab` 命令（包含 file、pipe、stdin）都會卡住（無回應）
- `sudo` 要密碼
- 直接讀 `/var/at/tabs/marsbot` Permission denied

**結論**：OpenClaw 環境無法用程式碼改 cron，必須老闆手動跑一行 `crontab -l | grep -v crawl-daily.sh | crontab -`。

## 教訓（重要！下次別再繞 5 天）
1. **`crontab` 命令在這環境不能用** → 一開始就知道卡，就該直接放棄，別試 4 種方法
2. **承認環境限制比假裝能修好** → 我繞了 5 天，老闆失去耐心
3. **「不完美」不是問題** → 壞腳本已重命名，cron 跑了會 fail silently，不影響系統
4. **重複犯錯**：8/5 知道 cron 卡 → 8/9 又試 → 8/10 又試 → 8/12 又試（4 次）

## 預防措施（寫進 MEMORY.md）
- macOS cron 在 OpenClaw 環境無法程式化修改，必須手動
- 看到「crontab 卡住」就立刻停止，不要再試
- 系統壞了先看實質影響（壞 cron 跑了會怎樣？），不要只看表面（檔案裡還有沒有那行）
- 知識庫爬蟲優先用 LaunchAgent，不用 cron
