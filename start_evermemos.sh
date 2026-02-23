#!/bin/bash
echo '=== Applying patches ==='

python3 << 'PATCHEND'
import re

# Read file
with open('/app/EverMemOS/src/memory_layer/llm/openai_provider.py', 'r') as f:
    content = f.read()

# Patch 1: Fix JSON parsing - find and replace the exact pattern
old_pattern = '                        test = b"".join(chunks).decode()\n                        response_data = json.loads(test)'
new_pattern = '''                        raw_response = b"".join(chunks).decode()
                        # Clean MiniMax response
                        if "</think>" in raw_response:
                            raw_response = raw_response.split("</think>")[-1]
                        # Find JSON
                        start = raw_response.find('{')
                        end = raw_response.rfind('}')
                        if start != -1 and end != -1 and end > start:
                            raw_response = raw_response[start:end+1].strip()
                        response_data = json.loads(raw_response)'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('/app/EverMemOS/src/memory_layer/llm/openai_provider.py', 'w') as f:
        f.write(content)
    print('Patch applied successfully')
else:
    print('Patch already applied or pattern not found')

# Patch 2: Remove provider field
if '"provider": openrouter_provider,' in content:
    content = content.replace('"provider": openrouter_provider,', '')
    with open('/app/EverMemOS/src/memory_layer/llm/openai_provider.py', 'w') as f:
        f.write(content)
    print('Provider field removed')
PATCHEND

echo '=== Starting EverMemOS ==='
cd /app/EverMemOS
exec /root/.local/bin/uv run python src/run.py --port 1995
