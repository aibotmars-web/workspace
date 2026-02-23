import os

memory_dir = "/Users/marsbot/.openclaw/workspace/memory/"
files = sorted(os.listdir(memory_dir))
for f in files:
    if f.endswith('.md'):
        print(f)
