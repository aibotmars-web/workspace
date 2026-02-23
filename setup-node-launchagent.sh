#!/bin/bash

# 建立 OpenClaw Node LaunchAgent
cat > ~/Library/LaunchAgents/ai.openclaw.node.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.node</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/openclaw</string>
        <string>node</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# 載入
launchctl load ~/Library/LaunchAgents/ai.openclaw.node.plist

echo "✅ OpenClaw Node 已設定為開機自動啟動"
