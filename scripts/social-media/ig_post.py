#!/usr/bin/env python3
"""
IG 自動發文腳本（instagrapi）
支援單張圖片 + 多圖 Carousel

用法：
  python3 ig_post.py --image card.jpg --caption "文案"
  python3 ig_post.py --images s1.jpg s2.jpg s3.jpg s4.jpg s5.jpg --caption "文案"

設定：
  export IG_USERNAME="你的IG帳號"
  export IG_PASSWORD="你的IG密碼"
  或放在 ~/.openclaw/workspace/scripts/social-media/ig_config.json
"""

import os
import sys
import json
import argparse
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "ig_config.json"
SESSION_PATH = Path(__file__).parent / "ig_session.json"


def load_config():
    """讀取 IG 帳號設定"""
    if os.environ.get("IG_USERNAME") and os.environ.get("IG_PASSWORD"):
        return {
            "username": os.environ["IG_USERNAME"],
            "password": os.environ["IG_PASSWORD"],
        }
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    print("❌ 找不到 IG 帳號設定！")
    print(f"   請建立 {CONFIG_PATH}：")
    print('   {"username": "你的帳號", "password": "你的密碼"}')
    print("   或設定環境變數 IG_USERNAME / IG_PASSWORD")
    sys.exit(1)


def get_client(config):
    """取得 instagrapi 客戶端（自動管理 session）"""
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, BadPassword

    cl = Client()
    cl.delay_range = [1, 3]

    # 嘗試載入已儲存的 session
    if SESSION_PATH.exists():
        try:
            cl.load_settings(SESSION_PATH)
            cl.login(config["username"], config["password"])
            cl.get_timeline_feed()
            print("✅ 使用已儲存的 Session 登入")
            return cl
        except LoginRequired:
            print("⚠️ Session 過期，重新登入...")
            SESSION_PATH.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Session 載入失敗：{e}，重新登入...")
            SESSION_PATH.unlink(missing_ok=True)

    # 全新登入
    try:
        print(f"🔐 登入 IG：{config['username']}")
        cl.login(config["username"], config["password"])
        cl.dump_settings(SESSION_PATH)
        print("✅ 登入成功，Session 已儲存")
        return cl
    except BadPassword:
        print("❌ 帳號或密碼錯誤")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 登入失敗：{e}")
        sys.exit(1)


def post_photo(image_path: str, caption: str, dry_run: bool = False) -> dict:
    """發布單張 IG 貼文"""
    if not os.path.exists(image_path):
        print(f"❌ 圖片不存在：{image_path}")
        sys.exit(1)

    if dry_run:
        print("🔍 [Dry Run] 不會實際發文")
        print(f"   圖片：{image_path}")
        print(f"   文案：{caption[:100]}...")
        return {"status": "dry_run", "image": image_path}

    config = load_config()
    cl = get_client(config)

    try:
        print(f"📤 發布單張貼文...")
        media = cl.photo_upload(path=image_path, caption=caption)
        result = {
            "status": "success",
            "media_id": str(media.id),
            "url": f"https://www.instagram.com/p/{media.code}/",
            "timestamp": media.taken_at.isoformat() if media.taken_at else "",
        }
        print(f"✅ 發文成功！")
        print(f"   網址：{result['url']}")
        return result
    except Exception as e:
        print(f"❌ 發文失敗：{e}")
        return {"status": "error", "error": str(e)}


def post_album(image_paths: list[str], caption: str, dry_run: bool = False) -> dict:
    """發布多圖 Carousel 貼文（album_upload）"""
    # 驗證所有圖片存在
    for p in image_paths:
        if not os.path.exists(p):
            print(f"❌ 圖片不存在：{p}")
            sys.exit(1)

    if dry_run:
        print("🔍 [Dry Run] 不會實際發文")
        print(f"   圖片數：{len(image_paths)} 張")
        for p in image_paths:
            print(f"     - {p}")
        print(f"   文案：{caption[:100]}...")
        return {"status": "dry_run", "images": image_paths}

    config = load_config()
    cl = get_client(config)

    try:
        print(f"📤 發布 Carousel（{len(image_paths)} 張）...")
        paths_obj = [Path(p) for p in image_paths]
        media = cl.album_upload(paths=paths_obj, caption=caption)
        result = {
            "status": "success",
            "media_id": str(media.id),
            "url": f"https://www.instagram.com/p/{media.code}/",
            "slide_count": len(image_paths),
        }
        print(f"✅ Carousel 發文成功！")
        print(f"   網址：{result['url']}")
        return result
    except Exception as e:
        print(f"❌ Carousel 發文失敗：{e}")
        # Fallback：嘗試只發第一張
        print("   ⚡ 嘗試發布第一張作為單圖...")
        return post_photo(image_paths[0], caption)


def main():
    parser = argparse.ArgumentParser(description="IG 自動發文")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="單張圖片路徑（JPG）")
    group.add_argument("--images", nargs="+", help="多張圖片路徑（Carousel，最多 10 張）")
    parser.add_argument("--caption", required=True, help="貼文文案")
    parser.add_argument("--dry-run", action="store_true", help="測試模式（不實際發文）")
    args = parser.parse_args()

    if args.images:
        if len(args.images) > 10:
            print("❌ Carousel 最多 10 張")
            sys.exit(1)
        result = post_album(args.images, args.caption, dry_run=args.dry_run)
    else:
        result = post_photo(args.image, args.caption, dry_run=args.dry_run)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("success", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
