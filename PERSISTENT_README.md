# OpenClaw 持久化配置

## 概述

所有套件預裝在 Docker 容器內，無需每次重新安裝。

## 預裝內容

| 項目 | 位置 | 說明 |
|------|------|------|
| Python MCP | `/usr/local/lib/python3.11/dist-packages/` | minimax-coding-plan-mcp |
| uvx | `/root/.local/bin/uvx` | Python 運行工具 |
| Node.js MCP | `/usr/local/lib/node_modules/` | @ameno/pi-minimax-mcp |

## 使用方式

### 方式 1：使用現有鏡像 + Volume（推薦）

```bash
# 創建 volume
docker volume create openclaw-python-packages
docker volume create openclaw-uv-bin
docker volume create openclaw-uv-cache
docker volume create openclaw-node-packages

# 啟動容器（挂载 volume）
docker run -d \
  --name openclaw-main \
  -p 18789:18789 \
  -v openclaw-python-packages:/usr/local/lib/python3.11/dist-packages \
  -v openclaw-uv-bin:/root/.local/bin \
  -v openclaw-uv-cache:/root/.cache/uv \
  -v openclaw-node-packages:/usr/local/lib/node_modules \
  -v ./workspace:/root/.openclaw/workspace \
  -v ./memory:/root/.openclaw/workspace/memory \
  openclaw/openclaw:latest
```

### 方式 2：使用 docker-compose

```bash
# 啟動所有服務
docker-compose -f docker-compose.persistent.yml up -d

# 查看日誌
docker-compose -f docker-compose.persistent.yml logs -f
```

### 方式 3：構建自定義鏡像（完全持久化）

```bash
# 構建鏡像
docker build -t openclaw-persistent:latest -f Dockerfile.persistent .

# 運行
docker run -d \
  --name openclaw-main \
  -p 18789:18789 \
  -v ./workspace:/root/.openclaw/workspace \
  -v ./memory:/root/.openclaw/workspace/memory \
  openclaw-persistent:latest
```

## 驗證

### 檢查 MCP 伺服器
```bash
docker exec openclaw-main ps aux | grep mcp
```

### 檢查 Python 套件
```bash
docker exec openclaw-main pip3 list | grep minimax
```

### 檢查 uvx
```bash
docker exec openclaw-main /root/.local/bin/uvx --version
```

## Volume 管理

```bash
# 列出所有 volume
docker volume ls | grep openclaw

# 備份 volume
docker run --rm -v openclaw-python-packages:/data -v $(pwd):/backup alpine tar czf /backup/python-packages.tar.gz -C /data .

# 恢復 volume
docker run --rm -v openclaw-python-packages:/data -v $(pwd):/backup alpine tar xzf /backup/python-packages.tar.gz -C /data
```

## 故障排除

### MCP 伺服器未啟動
```bash
docker exec openclaw-main cat /var/log/mcp.log
```

### 權限問題
```bash
docker exec openclaw-main chown -R 1000:1000 /root/.local/bin/
```

### 重新安裝套件
```bash
docker exec openclaw-main pip3 install --no-cache-dir minimax-coding-plan-mcp
docker exec openclaw-main npm install -g @ameno/pi-minimax-mcp
```
