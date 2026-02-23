# 沙盒隔離與 Supabase 同步系統

## 📊 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                      老闆需求                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Planner                                │
│            分配任務 → BD 追蹤 → 監督進度                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              沙盒隔離執行層（每個 Agent 獨立）               │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  coder   │  │ crawler  │  │  image   │  │ assistant│   │
│  │ (沙盒)   │  │ (沙盒)   │  │ (沙盒)   │  │ (沙盒)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                    │
│                         ▼                                    │
│              ┌─────────────────────┐                        │
│              │  Supabase 同步層    │                        │
│              │  （雲端統一儲存）   │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    所有 Agents 可查詢結果
```

---

## 🎯 功能清單

### 1. 自動創建沙盒目錄

```bash
# 當 Agent 首次執行任務時，自動創建：

~/.openclaw/
├── workspace-coder/           # coder 專屬工作區
│   ├── memory/
│   │   ├── tasks/            # 任務追蹤
│   │   ├── daily-summary.md  # 每日總結
│   │   └── knowledge-base.md # 知識庫
│   ├── projects/             # 專案檔案
│   └── .context              # 上下文載入點
│
├── workspace-crawler/         # crawler 專屬工作區
│   └── ...
│
├── workspace-image/           # image 專屬工作區
│   └── ...
│
└── workspace-trader/          # trader 專屬工作區
    └── ...
```

**創建腳本：**
```bash
#!/bin/bash
# create-sandbox.sh

AGENT_ID=$1

if [ -z "$AGENT_ID" ]; then
  echo "用法：./create-sandbox.sh <agent-id>"
  exit 1
fi

SANDBOX_DIR="$HOME/.openclaw/workspace-$AGENT_ID"

# 創建目錄結構
mkdir -p $SANDBOX_DIR/memory/tasks
mkdir -p $SANDBOX_DIR/projects
mkdir -p $SANDBOX_DIR/.context

# 初始化記憶檔
echo "# $AGENT_ID 記憶" > $SANDBOX_DIR/memory/tasks/.gitkeep
echo "# $AGENT_ID 每日總結" > $SANDBOX_DIR/memory/daily-summary.md
echo "# $AGENT_ID 上下文" > $SANDBOX_DIR/.context/current.json

# 設定權限
chmod 700 $SANDBOX_DIR
chmod 700 $SANDBOX_DIR/memory
chmod 700 $SANDBOX_DIR/.context

echo "✅ 沙盒創建完成：$SANDBOX_DIR"
```

---

### 2. 執行時自動載入上下文

```javascript
// context-loader.js
const fs = require('fs');
const path = require('path');

class ContextLoader {
  constructor(agentId) {
    this.agentId = agentId;
    this.sandboxDir = path.join(process.env.HOME, '.openclaw', `workspace-${agentId}`);
    this.contextFile = path.join(this.sandboxDir, '.context', 'current.json');
  }

  // 載入當前上下文
  load() {
    try {
      if (fs.existsSync(this.contextFile)) {
        const context = JSON.parse(fs.readFileSync(this.contextFile, 'utf8'));
        console.log(`📂 載入上下文：${this.agentId}`);
        return context;
      }
    } catch (e) {
      console.log(`⚠️ 上下文載入失敗：${e.message}`);
    }
    return { tasks: [], history: [], preferences: {} };
  }

  // 保存上下文
  save(context) {
    try {
      fs.writeFileSync(this.contextFile, JSON.stringify(context, null, 2));
      console.log(`💾 上下文已保存：${this.agentId}`);
    } catch (e) {
      console.log(`❌ 上下文保存失敗：${e.message}`);
    }
  }

  // 添加任務到上下文
  addTask(task) {
    const context = this.load();
    context.tasks.push({
      id: task.id,
      name: task.name,
      status: 'in_progress',
      startedAt: new Date().toISOString(),
      ...task
    });
    this.save(context);
  }

  // 更新任務狀態
  updateTask(taskId, updates) {
    const context = this.load();
    const taskIndex = context.tasks.findIndex(t => t.id === taskId);
    if (taskIndex !== -1) {
      context.tasks[taskIndex] = { ...context.tasks[taskIndex], ...updates };
      this.save(context);
    }
  }
}

module.exports = ContextLoader;
```

---

### 3. 定時同步到 Supabase

```javascript
// supabase-sync.js
const { createClient } from '@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Supabase 客戶端
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

class SupabaseSync {
  constructor(agentId) {
    this.agentId = agentId;
    this.sandboxDir = path.join(process.env.HOME, '.openclaw', `workspace-${agentId}`);
  }

  // 同步所有記憶
  async syncAll() {
    const results = {
      memories: await this.syncMemories(),
      tasks: await this.syncTasks(),
      status: await this.syncStatus()
    };
    return results;
  }

  // 同步對話濃縮
  async syncMemories() {
    const memoryDir = path.join(this.sandboxDir, 'memory');
    
    try {
      // 讀取所有 markdown 檔案
      const files = fs.readdirSync(memoryDir).filter(f => f.endsWith('.md'));
      
      for (const file of files) {
        const content = fs.readFileSync(path.join(memoryDir, file), 'utf8');
        
        const { error } = await supabase
          .from('memories')
          .upsert({
            agent_id: this.agentId,
            file_name: file,
            content: content,
            synced_at: new Date().toISOString()
          }, { onConflict: 'agent_id, file_name' });
        
        if (error) throw error;
      }
      
      return { success: true, files: files.length };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  // 同步任務狀態
  async syncTasks() {
    try {
      const tasksDir = path.join(this.sandboxDir, 'memory', 'tasks');
      
      // 讀取 BD 任務
      const { execSync } = require('child_process');
      const bdOutput = execSync('bd list --json', { encoding: 'utf8' });
      const tasks = JSON.parse(bdOutput);
      
      const { error } = await supabase
        .from('task_logs')
        .upsert({
          agent_id: this.agentId,
          tasks: tasks,
          synced_at: new Date().toISOString()
        }, { onConflict: 'agent_id' });
      
      if (error) throw error;
      
      return { success: true, count: tasks.length };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  // 同步 Agent 狀態
  async syncStatus() {
    try {
      const status = {
        agent_id: this.agentId,
        status: 'active',
        last_active: new Date().toISOString(),
        sandbox_dir: this.sandboxDir
      };
      
      const { error } = await supabase
        .from('agents_status')
        .upsert(status, { onConflict: 'agent_id' });
      
      if (error) throw error;
      
      return { success: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  // 濃縮對話（每 10 句話）
  async summarizeConversation(conversation) {
    // 簡單濃縮：保留要點
    const summary = {
      agent_id: this.agentId,
      original_length: conversation.length,
      summary: conversation.slice(-20).join('\n'),  # 保留最近 20 句
      summarized_at: new Date().toISOString()
    };
    
    const { error } = await supabase
      .from('conversation_summaries')
      .insert(summary);
    
    if (error) throw error;
    
    return summary;
  }
}

module.exports = SupabaseSync;
```

---

### 4. 完整整合腳本

```bash
#!/bin/bash
# sandbox-manager.sh

AGENT_ID=$1
ACTION=$2

SANDBOX_DIR="$HOME/.openclaw/workspace-$AGENT_ID"

case $ACTION in
  create)
    echo "🔧 創建沙盒：$AGENT_ID"
    
    mkdir -p $SANDBOX_DIR/memory/tasks
    mkdir -p $SANDBOX_DIR/projects
    mkdir -p $SANDBOX_DIR/.context
    
    # 初始化
    echo "# $AGENT_ID 記憶" > $SANDBOX_DIR/memory/README.md
    echo "{}" > $SANDBOX_DIR/.context/current.json
    
    chmod -R 700 $SANDBOX_DIR
    
    echo "✅ 沙盒創建完成"
    ;;
    
  sync)
    echo "☁️ 同步到 Supabase：$AGENT_ID"
    
    node ~/bin/supabase-sync.js $AGENT_ID
    
    echo "✅ 同步完成"
    ;;
    
  load-context)
    echo "📂 載入上下文：$AGENT_ID"
    
    node ~/bin/context-loader.js $AGENT_ID load
    
    ;;
    
  save-context)
    echo "💾 保存上下文：$AGENT_ID"
    
    node ~/bin/context-loader.js $AGENT_ID save
    
    ;;
    
  *)
    echo "用法：./sandbox-manager.sh <agent-id> <action>"
    echo "動作：create | sync | load-context | save-context"
    ;;
esac
```

---

## 📊 Cron 定時同步

```json
{
  "jobs": [
    {
      "id": "sandbox-sync-coder",
      "name": "Coder 沙盒同步",
      "schedule": { "kind": "cron", "expr": "*/15 * * * *", "tz": "Asia/Taipei" },
      "sessionTarget": "isolated",
      "agentId": "coder",
      "payload": {
        "kind": "agentTurn",
        "message": "執行沙盒同步：\n1. 讀取 workspace-coder/memory/ 中所有任務進度\n2. 濃縮最近對話（每 10 句話）\n3. 同步到 Supabase（task_logs 表）\n4. 回報同步結果"
      }
    },
    {
      "id": "sandbox-sync-crawler",
      "name": "Crawler 沙盒同步",
      "schedule": { "kind": "cron", "expr": "*/15 * * * *", "tz": "Asia/Taipei" },
      "sessionTarget": "isolated",
      "agentId": "crawler",
      "payload": {
        "kind": "agentTurn",
        "message": "執行沙盒同步：\n1. 讀取 workspace-crawler/memory/ 中所有任務進度\n2. 濃縮最近對話\n3. 同步到 Supabase\n4. 回報同步結果"
      }
    }
  ]
}
```

---

## 🎯 使用流程

### 新任務執行時

```bash
# Step 1: 載入上下文
./sandbox-manager.sh coder load-context

# Step 2: 執行任務
# ... (Agent 執行工作)

# Step 3: 保存上下文
./sandbox-manager.sh coder save-context

# Step 4: 同步到雲端
./sandbox-manager.sh coder sync
```

### 每日定時執行

```bash
# 每 15 分鐘自動同步
# 設定在 Cron Job 中
```

---

## 📋 與 BD 整合

| BD 命令 | 沙盒動作 |
|---------|---------|
| `bd create "任務"` | → 寫入 sandbox/memory/tasks/ |
| `bd update --status` | → 更新 sandbox/.context/current.json |
| `bd list` | → 讀取 sandbox/memory/tasks/ |
| `bd close` | → 同步到 Supabase + 從沙盒移除 |

---

## ✅ 優勢

| 功能 | 效果 |
|------|------|
| 沙盒隔離 | Agent 執行環境獨立，不互相干擾 |
| 自動載入 | 每次執行自動讀取上下文 |
| 定時同步 | 每 15 分鐘備份到雲端 |
| 濃縮機制 | 每 10 句話自動濃縮，節省空間 |
| 快速恢復 | 當機後可從 Supabase 恢復 |

---

## 🚀 下一步

1. **創建腳本檔案**
   - `create-sandbox.sh`
   - `context-loader.js`
   - `supabase-sync.js`
   - `sandbox-manager.sh`

2. **設定 Cron 同步**
   - 每 15 分鐘同步一次

3. **更新 Agents 配置**
   - 加入沙盒路徑
   - 加入載入腳本

---

## 📞 狀態

**待實作：** 腳本編寫 + Cron 設定
**需要：** 老闆確認是否開始實作
