#!/usr/bin/env python3
"""
IG 留言 & 私訊監控 + AI 回覆草稿
功能：
  - 抓最近貼文的留言 → AI 幫你想幽默有梗的回覆
  - 抓私訊收件匣 → AI 草稿回覆
  - 顯示給老闆確認，輸入 y/n/s 決定發/跳過/自訂

用法：
  python3 ig_comments.py --account money.showtime
  python3 ig_comments.py --account bossmaker.lab --dm    # 也看私訊
  python3 ig_comments.py --account money.showtime --auto  # 全自動（危險！）
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

IG_CONFIGS = {
    "money.showtime":  SCRIPT_DIR / "ig_config.json",
    "bossmaker.lab":   SCRIPT_DIR / "startup_ig_config.json",
}

CHANNEL_STYLE = {
    "money.showtime": "幣圈財經帳號（89 風格，幽默但有料）",
    "bossmaker.lab":  "創業新創帳號（有梗有深度，接地氣）",
}


def call_ai(prompt: str, timeout: int = 45) -> str:
    """用 openclaw AI 生成回覆草稿"""
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--agent", "main", "--json", "--message", prompt],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            payloads = data.get("result", {}).get("payloads", [])
            if payloads and payloads[0].get("text"):
                return payloads[0]["text"].strip()
    except Exception as e:
        print(f"   ⚠️ AI 失敗：{e}")
    return ""


def get_client(account: str):
    """取得 instagrapi 客戶端"""
    from instagrapi import Client

    config_path = IG_CONFIGS.get(account)
    if not config_path or not config_path.exists():
        print(f"❌ 找不到 {account} 的設定檔")
        sys.exit(1)

    config = json.loads(config_path.read_text())
    username = config.get("username", "")
    password = config.get("password", "")

    cl = Client()
    cl.delay_range = [1, 3]

    session_path = SCRIPT_DIR / f"ig_session_{account.replace('.', '_')}.json"
    if session_path.exists():
        try:
            cl.load_settings(session_path)
            cl.login(username, password)
            cl.get_timeline_feed()
            print(f"✅ 登入 @{username}")
            return cl
        except Exception:
            session_path.unlink(missing_ok=True)

    cl.login(username, password)
    cl.dump_settings(session_path)
    print(f"✅ 登入成功 @{username}")
    return cl


def draft_comment_reply(comment_text: str, account: str, post_topic: str = "") -> str:
    """AI 生成留言回覆草稿"""
    style = CHANNEL_STYLE.get(account, "台灣網路風格")
    topic_hint = f"這篇貼文關於：{post_topic}\n" if post_topic else ""
    prompt = f"""你是台灣 IG {style} 的小編在回覆留言。
{topic_hint}
有粉絲留言：「{comment_text}」

請用台灣口語、幽默有梗、接地氣的方式回覆。
要求：
- 字數 15-40 字
- 不要 AI 腔
- 不要過度禮貌（不要「您好」「非常感謝」那種）
- 如果留言很短或只是 emoji，可以用幽默方式互動
- 不要提博弈、賭博（帳號形象是財經資訊）
- 如果是批評，輕鬆反駁或認同也行

只輸出回覆內容，不要解釋。"""

    return call_ai(prompt)


def draft_dm_reply(dm_text: str, sender: str, account: str) -> str:
    """AI 生成私訊回覆草稿"""
    style = CHANNEL_STYLE.get(account, "台灣網路風格")
    prompt = f"""你是台灣 IG {style} 的小編在回覆私訊。
用戶「{sender}」傳來：「{dm_text}」

請用台灣口語、自然不做作的方式回覆。
要求：
- 字數 20-60 字
- 像朋友在聊天，不要 AI 腔
- 如果是詢問投資建議，說「我們帳號只提供資訊，投資請謹慎」但要說得自然
- 如果是廣告或垃圾訊息，可以說不感興趣
- 不要提博弈賭博

只輸出回覆內容，不要解釋。"""

    return call_ai(prompt)


def process_comments(cl, account: str, limit: int = 5, auto: bool = False):
    """處理最近貼文的留言"""
    print(f"\n{'='*50}")
    print(f"💬 留言回覆模式")
    print(f"{'='*50}")

    # 取得最近 3 篇貼文
    user_id = cl.user_id_from_username(account.split("@")[-1])
    medias = cl.user_medias(user_id, amount=3)

    if not medias:
        print("❌ 沒有找到貼文")
        return

    replied = 0
    for media in medias:
        if replied >= limit:
            break

        print(f"\n📸 貼文：{media.caption_text[:50] if media.caption_text else '(無文案)'}...")
        post_topic = media.caption_text[:80] if media.caption_text else ""
        comments = cl.media_comments(media.id, amount=10)

        for comment in comments:
            if replied >= limit:
                break

            username = comment.user.username
            text = comment.text

            # 跳過自己的留言
            if username == account.split("@")[-1]:
                continue
            # 跳過太短的（純 emoji 或 1 字）
            if len(text) < 2:
                continue

            print(f"\n  👤 @{username}：{text}")

            # AI 起草回覆
            print("  🤖 AI 起草中...", end="", flush=True)
            draft = draft_comment_reply(text, account, post_topic)
            print(f"\r  💡 草稿：{draft}")

            if not draft:
                print("  ⚠️ AI 無法生成，跳過")
                continue

            if auto:
                # 全自動發出（不推薦）
                cl.media_comment(media.id, draft)
                print(f"  ✅ 已自動回覆")
                replied += 1
            else:
                # 人工確認
                print("  [y] 發出  [n] 跳過  [s] 自訂  [q] 離開")
                try:
                    choice = input("  選擇：").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n已中止")
                    return

                if choice == "q":
                    return
                elif choice == "y":
                    cl.media_comment(media.id, draft)
                    print("  ✅ 已回覆！")
                    replied += 1
                elif choice == "s":
                    try:
                        custom = input("  輸入自訂回覆：").strip()
                        if custom:
                            cl.media_comment(media.id, custom)
                            print("  ✅ 已回覆！")
                            replied += 1
                    except (EOFError, KeyboardInterrupt):
                        return
                else:
                    print("  ⏭️  跳過")

    print(f"\n✅ 完成！共回覆 {replied} 則留言")


def process_dms(cl, account: str, limit: int = 5, auto: bool = False):
    """處理私訊收件匣"""
    print(f"\n{'='*50}")
    print(f"📩 私訊回覆模式")
    print(f"{'='*50}")

    try:
        threads = cl.direct_threads(amount=10)
    except Exception as e:
        print(f"❌ 無法讀取私訊：{e}")
        return

    replied = 0
    for thread in threads:
        if replied >= limit:
            break
        if not thread.messages:
            continue

        # 取最新一則訊息
        last_msg = thread.messages[0]
        if not hasattr(last_msg, "text") or not last_msg.text:
            continue

        # 跳過自己發的
        sender_id = str(last_msg.user_id)
        my_id = str(cl.user_id)
        if sender_id == my_id:
            continue

        # 取發送者名稱
        sender_username = "用戶"
        for user in thread.users:
            if str(user.pk) == sender_id:
                sender_username = user.username
                break

        text = last_msg.text
        print(f"\n  📩 @{sender_username}：{text[:60]}")

        print("  🤖 AI 起草中...", end="", flush=True)
        draft = draft_dm_reply(text, sender_username, account)
        print(f"\r  💡 草稿：{draft}")

        if not draft:
            continue

        if auto:
            cl.direct_answer(thread.id, draft)
            print("  ✅ 已自動回覆")
            replied += 1
        else:
            print("  [y] 發出  [n] 跳過  [s] 自訂  [q] 離開")
            try:
                choice = input("  選擇：").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return

            if choice == "q":
                return
            elif choice == "y":
                cl.direct_answer(thread.id, draft)
                print("  ✅ 已回覆！")
                replied += 1
            elif choice == "s":
                try:
                    custom = input("  輸入自訂回覆：").strip()
                    if custom:
                        cl.direct_answer(thread.id, custom)
                        print("  ✅ 已回覆！")
                        replied += 1
                except (EOFError, KeyboardInterrupt):
                    return
            else:
                print("  ⏭️  跳過")

    print(f"\n✅ 完成！共回覆 {replied} 則私訊")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IG 留言 & 私訊 AI 回覆助手")
    parser.add_argument("--account", default="money.showtime",
                        choices=["money.showtime", "bossmaker.lab"],
                        help="要操作的 IG 帳號")
    parser.add_argument("--dm", action="store_true", help="也處理私訊")
    parser.add_argument("--limit", type=int, default=5, help="最多回覆幾則（預設 5）")
    parser.add_argument("--auto", action="store_true",
                        help="全自動發出（不需確認，有封號風險，不推薦）")
    args = parser.parse_args()

    if args.auto:
        print("⚠️  [全自動模式] 留言將不經確認直接發出，有封號風險！")
        print("   建議只用在測試，正式使用請拿掉 --auto")

    try:
        from instagrapi import Client
    except ImportError:
        print("❌ 請先安裝：pip install instagrapi")
        sys.exit(1)

    cl = get_client(args.account)
    process_comments(cl, args.account, limit=args.limit, auto=args.auto)

    if args.dm:
        process_dms(cl, args.account, limit=args.limit, auto=args.auto)
