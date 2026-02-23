#!/usr/bin/env python3
"""
OpenClaw Memory Sync Script
==========================
Syncs OpenClaw's memory files to EverMemOS for long-term storage.

Usage:
    python3 sync_to_evermemos.py --dry-run  # Test without actually syncing
    python3 sync_to_evermemos.py             # Actual sync
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from openclaw_evermemos import store_memory, retrieve_memories

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE_DIR / "memory"

def load_memory_files():
    """Load all memory files from workspace."""
    memories = []
    
    # Load daily memory files
    if MEMORY_DIR.exists():
        for md_file in MEMORY_DIR.glob("*.md"):
            if md_file.name != "MEMORY.md":
                print(f"📄 Loading: {md_file.name}")
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    memories.append({
                        "source": "daily_memory",
                        "file": md_file.name,
                        "content": content,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                    })
    
    # Load MEMORY.md
    memory_file = WORKSPACE_DIR / "MEMORY.md"
    if memory_file.exists():
        print(f"📄 Loading: MEMORY.md")
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            memories.append({
                "source": "long_term_memory",
                "file": "MEMORY.md",
                "content": content,
                "modified": datetime.fromtimestamp(memory_file.stat().st_mtime).isoformat()
            })
    
    return memories

def sync_to_evermemos(memories, dry_run=False):
    """Sync memories to EverMemOS."""
    
    print(f"\n🔄 Starting sync to EverMemOS...")
    print(f"📊 Total memories to sync: {len(memories)}")
    
    if dry_run:
        print("🧪 DRY RUN - No changes will be made\n")
    else:
        print("⚠️  LIVE MODE - Changes will be persisted\n")
    
    synced_count = 0
    
    for memory in memories:
        print(f"📤 Syncing: {memory['file']}")
        print(f"   Source: {memory['source']}")
        print(f"   Size: {len(memory['content'])} characters")
        
        if not dry_run:
            # Store each memory as a chunk
            chunk_size = 2000  # Split into manageable chunks
            chunks = [
                memory['content'][i:i+chunk_size] 
                for i in range(0, len(memory['content']), chunk_size)
            ]
            
            for idx, chunk in enumerate(chunks):
                result = store_memory(
                    message=f"[{memory['source']}] {memory['file']}\n\n{chunk}",
                    user_id="openclaw_sync",
                    group_id=f"memory_sync_{memory['source']}",
                    group_name=f"OpenClaw {memory['source']}",
                    role="assistant"
                )
                
                if result.get("status") == "ok":
                    synced_count += 1
                    print(f"   ✅ Chunk {idx+1}/{len(chunks)} synced")
                else:
                    print(f"   ❌ Chunk {idx+1} failed: {result}")
                    break
        else:
            print(f"   🧪 Would sync {len(memory['content']) // 2000 + 1} chunks")
    
    print(f"\n✅ Sync complete!")
    print(f"📊 Total chunks synced: {synced_count}")
    
    return synced_count

def main():
    parser = argparse.ArgumentParser(
        description="Sync OpenClaw memories to EverMemOS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test sync without making changes"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 OpenClaw → EverMemOS Memory Sync")
    print("=" * 60)
    
    # Load memories
    print("\n📂 Loading memory files...")
    memories = load_memory_files()
    
    if not memories:
        print("❌ No memory files found!")
        return
    
    print(f"✅ Found {len(memories)} memory files\n")
    
    # Sync to EverMemOS
    synced = sync_to_evermemos(memories, dry_run=args.dry_run)
    
    print("\n" + "=" * 60)
    print(f"✨ Sync complete! {synced} chunks synced to EverMemOS.")
    print("=" * 60)

if __name__ == "__main__":
    main()
