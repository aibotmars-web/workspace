# Docker 沙箱 (Docker Sandbox)

## 用途
- 隔離環境運行服務
- 測試不受影響的環境

## 常用指令

```bash
# 啟動容器
docker start <container>

# 停止容器
docker stop <container>

# 查看日誌
docker logs <container>

# 進入容器
docker exec -it <container> bash
```

## 問題處理

### 常見錯誤
- 鏡像不存在
- 端口衝突
- 權限問題

---

*更新：2026-02-24*
