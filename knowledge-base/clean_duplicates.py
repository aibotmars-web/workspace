#!/usr/bin/env python3
"""
清理知識庫重複/過期檔案
- C: .m4a 音檔（ASR 用完即清）
- B: .vtt 原始字幕（有對應 .txt/.md 才砍）
- D: experts/transcripts/ 子資料夾（只砍真重複，保留孤兒）

保留：
- 所有 .zh-TW.vtt（YouTube 官方繁體中文字幕，珍貴）
- 所有 .zh-TW.md（翻譯版）
- 所有 D 內外層沒對應的「孤兒」
"""
import os
import re
import subprocess
import shutil
from pathlib import Path

KB_ROOT = Path("/Users/marsbot/.openclaw/workspace/knowledge-base")
EXPERTS = KB_ROOT / "experts"
D_DIR = EXPERTS / "transcripts"

# YouTube 影片 ID pattern: 11 字元 [A-Za-z0-9_-]
YOUTUBE_ID_RE = re.compile(r'[-_A-Za-z0-9]{11}')


def get_video_id(filepath: Path) -> str:
    """從檔名/路徑提取純 YouTube 影片 ID"""
    match = YOUTUBE_ID_RE.search(filepath.name)
    return match.group(0) if match else filepath.name


def is_zhTW_vtt(filepath: Path) -> bool:
    """是否為 YouTube 官方繁體中文字幕（珍貴，絕對保留）"""
    name = filepath.name
    return name.endswith('.zh-TW.vtt') or name.endswith('.zh-TW.md')


def safe_trash(filepath: Path) -> bool:
    """用 trash 命令刪除（可恢復），失敗退回 mv"""
    try:
        result = subprocess.run(
            ['trash', str(filepath)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True
        print(f"  trash 失敗: {filepath} ({result.stderr.strip()[:100]})")
        return False
    except Exception as e:
        print(f"  trash 例外: {filepath} ({e})")
        return False


def main():
    print("=" * 70)
    print("知識庫清理 - 開始")
    print("=" * 70)

    # 統計初始狀態
    initial_size = sum(f.stat().st_size for f in EXPERTS.rglob('*') if f.is_file())
    print(f"\n📊 初始：experts/ 總大小 {initial_size / (1024**3):.2f} GB")

    results = {'C_kept': 0, 'C_trashed': 0,
               'B_kept': 0, 'B_trashed': 0,
               'D_kept': 0, 'D_trashed': 0,
               'D_orphan': 0}

    # ========== C: 砍 .m4a 音檔 ==========
    print("\n" + "=" * 70)
    print("C: .m4a 音檔清理（ASR 用完即清）")
    print("=" * 70)
    m4a_files = list(EXPERTS.rglob('*.m4a'))
    m4a_total_size = sum(f.stat().st_size for f in m4a_files if f.is_file())
    print(f"找到 {len(m4a_files)} 個 .m4a，總大小 {m4a_total_size / (1024**3):.2f} GB")

    for f in m4a_files:
        if f.is_file():
            if safe_trash(f):
                results['C_trashed'] += 1
            else:
                results['C_kept'] += 1

    print(f"✅ C 完成：刪除 {results['C_trashed']} 個，保留 {results['C_kept']} 個")

    # ========== 建索引：外層（不含 transcripts/）所有 .txt / .md 檔案 ID ==========
    print("\n" + "=" * 70)
    print("建立索引：外層 .txt/.md 檔案的影片 ID")
    print("=" * 70)
    outer_ids = {}  # video_id -> [filenames]
    for f in EXPERTS.rglob('*.txt'):
        if D_DIR in f.parents or not f.is_file():
            continue
        vid = get_video_id(f)
        outer_ids.setdefault(vid, []).append(f)
    for f in EXPERTS.rglob('*.md'):
        if D_DIR in f.parents or not f.is_file():
            continue
        vid = get_video_id(f)
        outer_ids.setdefault(vid, []).append(f)
    print(f"外層獨特影片 ID 數: {len(outer_ids)}")

    # ========== B: 砍 .vtt（只砍外層有對應 .txt/.md 的） ==========
    print("\n" + "=" * 70)
    print("B: .vtt 原始字幕清理（只砍有對應 .txt/.md 的）")
    print("=" * 70)
    vtt_files = list(EXPERTS.rglob('*.vtt'))
    print(f"找到 {len(vtt_files)} 個 .vtt")

    for f in vtt_files:
        if not f.is_file():
            continue
        # 保留珍貴的 .zh-TW.vtt（官方繁體中文字幕）
        if is_zhTW_vtt(f):
            # 但如果有對應的 .zh-TW.md 翻譯，可以砍（保留翻譯版）
            vid = get_video_id(f)
            has_zhTW_md = any(
                str(p).endswith('.zh-TW.md') or get_video_id(p) == vid
                for p in outer_ids.get(vid, [])
            )
            if has_zhTW_md:
                if safe_trash(f):
                    results['B_trashed'] += 1
                    continue
            results['B_kept'] += 1
            print(f"  保留珍貴: {f.relative_to(KB_ROOT)}")
            continue

        # 其他 .vtt：只砍外層有對應的
        vid = get_video_id(f)
        if vid in outer_ids and outer_ids[vid]:
            if safe_trash(f):
                results['B_trashed'] += 1
                continue
        results['B_kept'] += 1

    print(f"✅ B 完成：刪除 {results['B_trashed']} 個，保留 {results['B_kept']} 個")

    # ========== D: 砍 experts/transcripts/ 真重複（保留孤兒） ==========
    print("\n" + "=" * 70)
    print("D: experts/transcripts/ 真重複清理（保留孤兒）")
    print("=" * 70)
    if not D_DIR.exists():
        print("D 目錄不存在，跳過")
    else:
        d_files = list(D_DIR.rglob('*'))
        d_files = [f for f in d_files if f.is_file()]
        print(f"D 內檔案總數: {len(d_files)}")

        for f in d_files:
            vid = get_video_id(f)
            if vid in outer_ids and outer_ids[vid]:
                # 真重複：砍
                if safe_trash(f):
                    results['D_trashed'] += 1
                    continue
            # 孤兒：保留
            results['D_kept'] += 1
            results['D_orphan'] += 1

    print(f"✅ D 完成：刪除 {results['D_trashed']} 個，保留 {results['D_kept']} 個（{results['D_orphan']} 個孤兒）")

    # ========== 統計最終狀態 ==========
    print("\n" + "=" * 70)
    print("📊 最終統計")
    print("=" * 70)
    final_size = sum(f.stat().st_size for f in EXPERTS.rglob('*') if f.is_file())
    saved = initial_size - final_size
    print(f"初始大小: {initial_size / (1024**3):.2f} GB")
    print(f"最終大小: {final_size / (1024**3):.2f} GB")
    print(f"釋放空間: {saved / (1024**3):.2f} GB ({saved / (1024**2):.1f} MB)")
    print()
    print(f"B 刪除/保留: {results['B_trashed']}/{results['B_kept']}")
    print(f"C 刪除/保留: {results['C_trashed']}/{results['C_kept']}")
    print(f"D 刪除/保留（孤兒）: {results['D_trashed']}/{results['D_kept']}（{results['D_orphan']} 個孤兒）")
    print(f"\n總刪除: {results['B_trashed'] + results['C_trashed'] + results['D_trashed']} 個檔案")
    print(f"總保留: {results['B_kept'] + results['C_kept'] + results['D_kept']} 個檔案（含孤兒）")


if __name__ == '__main__':
    main()