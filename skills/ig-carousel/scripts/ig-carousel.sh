#!/bin/bash
# ig-carousel - IG Carousel 自動發文 CLI wrapper
# 用法：ig-carousel <command> [channel]

PIPELINE="$HOME/.openclaw/workspace/scripts/social-media/content_pipeline.py"
CARDS_DIR="$HOME/.openclaw/workspace/agents/assistant-work/cards"
HISTORY="$HOME/.openclaw/workspace/scripts/social-media/posted_history.json"

# API Keys
export FAL_KEY="${FAL_KEY:-aaac8b5c-6758-4ad2-9770-878ceccceb92:aaec977e4232a0cb61ca9363dc11a9de}"

COMMAND="${1:-help}"
CHANNEL="${2:-crypto}"

case "$COMMAND" in
  post)
    echo "📸 [ig-carousel] 完整發文流程：$CHANNEL"
    echo "   Step 1/3: Pipeline 生成..."
    cd "$HOME/.openclaw/workspace/scripts/social-media"
    python3 "$PIPELINE" --channel "$CHANNEL"
    ;;

  draft)
    echo "📝 [ig-carousel] 生成草稿：$CHANNEL"
    cd "$HOME/.openclaw/workspace/scripts/social-media"
    python3 "$PIPELINE" --channel "$CHANNEL" --dry-run
    ;;

  publish)
    echo "📤 [ig-carousel] 發布上次草稿：$CHANNEL"
    cd "$HOME/.openclaw/workspace/scripts/social-media"
    python3 "$PIPELINE" --channel "$CHANNEL" --publish-last
    ;;

  select-cover)
    N="${3:-1}"
    echo "🖼️ [ig-carousel] 套用封面候選 $N：$CHANNEL"
    cd "$HOME/.openclaw/workspace/scripts/social-media"
    python3 "$PIPELINE" --channel "$CHANNEL" --select-cover "$N"
    ;;

  preview)
    echo "👀 [ig-carousel] 最新草稿預覽"
    LATEST=$(ls -td "$CARDS_DIR/${CHANNEL}_"* 2>/dev/null | grep -v FAILED | head -1)
    if [ -z "$LATEST" ]; then
      echo "❌ 找不到 $CHANNEL 的草稿"
      exit 1
    fi
    echo "   📁 目錄：$(basename $LATEST)"
    echo "   📸 圖片：$(ls "$LATEST"/*.jpg 2>/dev/null | wc -l | tr -d ' ') 張"
    if [ -f "$LATEST/caption.txt" ]; then
      echo "   📝 文案預覽："
      head -5 "$LATEST/caption.txt"
      echo "   ..."
    fi
    if [ -f "$LATEST/article_meta.json" ]; then
      echo "   📰 文章："
      cat "$LATEST/article_meta.json"
    fi
    ;;

  history)
    echo "📊 [ig-carousel] 發文歷史"
    if [ -f "$HISTORY" ]; then
      python3 -c "
import json
h = json.loads(open('$HISTORY').read())
print(f'共 {len(h)} 筆紀錄\n')
for e in h[-10:]:
    print(f\"  [{e.get('channel','')}] {e.get('posted_at','')[:16]}\")
    print(f\"    {e.get('hook', e.get('title',''))[:60]}\")
    print()
"
    else
      echo "   (尚無發文紀錄)"
    fi
    ;;

  help|--help|-h)
    echo "📸 ig-carousel - IG Carousel 自動發文系統"
    echo ""
    echo "用法："
    echo "  ig-carousel post [channel]              完整發文（直接跑，不選封面）"
    echo "  ig-carousel draft [channel]             生成草稿 + 3 張封面候選"
    echo "  ig-carousel select-cover [channel] [N]  套用第 N 張封面候選（1-3）"
    echo "  ig-carousel publish [channel]           發布上次草稿"
    echo "  ig-carousel preview [channel]           預覽最新草稿"
    echo "  ig-carousel history                     查看發文歷史"
    echo ""
    echo "頻道：crypto（預設）、finance、startup"
    echo ""
    echo "推薦流程："
    echo "  1. ig-carousel draft crypto              生成草稿 + 3 封面候選"
    echo "  2. understand_image 看封面 → 通知老闆選"
    echo "  3. ig-carousel select-cover crypto 2     套用選中的封面"
    echo "  4. humanizer + Hook 優化 caption.txt"
    echo "  5. ig-carousel publish crypto            發布"
    ;;

  *)
    echo "❌ 未知指令：$COMMAND"
    echo "   用 'ig-carousel help' 查看用法"
    exit 1
    ;;
esac
