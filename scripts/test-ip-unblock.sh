#!/bin/bash
# 测试 YouTube IP 是否解封

result=$(python3 -c "
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
try:
    t = api.fetch(video_id='KQ0wvtxsN-g', languages=['zh-TW'])
    print('SUCCESS')
except Exception as e:
    if 'IpBlocked' in str(e):
        print('BLOCKED')
    else:
        print('ERROR')
" 2>/dev/null)

if [ "$result" = "SUCCESS" ]; then
    echo "🎉 YouTube IP 已解封！可以继续抓字幕了"
    # 这里可以加发送通知的代码
else
    echo "⏳ IP 仍被封，等待进一步..."
fi
