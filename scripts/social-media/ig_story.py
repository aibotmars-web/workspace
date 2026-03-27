#!/usr/bin/env python3
"""
IG 自動限動 + 投票腳本
功能：生成限動圖片 → 加投票貼紙 → 發布到 IG

用法：
  python3 ig_story.py --channel crypto
  python3 ig_story.py --channel finance
  python3 ig_story.py --channel startup
  python3 ig_story.py --channel crypto --question "BTC今天？" --yes "📈漲" --no "📉跌"

設計：
  crypto/finance → 黑金財經風格 投票題目隨頻道自動產生
  startup        → 極簡黑白風格
"""

import os
import sys
import json
import argparse
import textwrap
import hashlib
import subprocess
from io import BytesIO
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# ── 設定 ─────────────────────────────────────────────────────
IG_CONFIG_MAP = {
    "crypto":  SCRIPT_DIR / "ig_config.json",
    "finance": SCRIPT_DIR / "ig_config.json",
    "startup": SCRIPT_DIR / "startup_ig_config.json",
}

# 每個頻道預設的每日投票題目（自動輪換）
DAILY_POLLS = {
    "crypto": [
        {"question": "BTC 今天走勢？",    "yes": "📈 衝衝衝", "no": "📉 修正中"},
        {"question": "你有在持幣嗎？",     "yes": "💰 有持倉", "no": "😅 空手等"},
        {"question": "ETH 會追上 BTC？",  "yes": "🔥 一定會", "no": "⏳ 還早咧"},
        {"question": "這波牛市才剛開始？", "yes": "🚀 才熱身", "no": "😬 快結束了"},
        {"question": "你相信 BTC 10萬？", "yes": "✅ 絕對到", "no": "🤔 不確定"},
        {"question": "現在是買幣好時機？", "yes": "💎 梭哈！", "no": "⏰ 等等再看"},
        {"question": "穩定幣你在用嗎？",   "yes": "💵 有在用", "no": "❌ 沒在碰"},
    ],
    "finance": [
        {"question": "台股今天漲嗎？",     "yes": "📈 噴", "no": "📉 拉"},
        {"question": "你有在買美股嗎？",   "yes": "🇺🇸 有", "no": "🏠 沒有"},
        {"question": "AI 股票還能買？",    "yes": "🤖 繼續", "no": "😰 泡沫了"},
        {"question": "今年會降息幾次？",   "yes": "3次以上", "no": "2次以下"},
    ],
    "startup": [
        {"question": "你有創業夢嗎？",     "yes": "🔥 一直有", "no": "😅 想想就好"},
        {"question": "AI 會取代你的工作？", "yes": "😱 會啊", "no": "💪 不會"},
        {"question": "你是打工還是創業？", "yes": "💼 打工人", "no": "🚀 創業中"},
        {"question": "副業有在賺嗎？",     "yes": "💰 有賺", "no": "😭 虧"},
    ],
}

THEMES = {
    "crypto":  {"accent": (247, 183, 49), "overlay": (0, 0, 0),  "min_a": 160, "max_a": 230, "name": "幣圈"},
    "finance": {"accent": (247, 183, 49), "overlay": (0, 5, 15), "min_a": 160, "max_a": 230, "name": "金融"},
    "startup": {"accent": (220, 175, 105),"overlay": (5, 5, 8),  "min_a": 170, "max_a": 245, "name": "創業"},
}

FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_poll_for_today(channel: str) -> dict:
    polls = DAILY_POLLS.get(channel, DAILY_POLLS["crypto"])
    day_of_year = datetime.now().timetuple().tm_yday
    return polls[day_of_year % len(polls)]


def make_story_image(channel: str, question: str, yes_text: str, no_text: str,
                     out_path: str) -> str:
    """生成 9:16 限動底圖（1080x1920）"""
    W, H = 1080, 1920
    theme = THEMES.get(channel, THEMES["crypto"])
    accent = theme["accent"]

    # 深色漸層背景
    bg = Image.new("RGB", (W, H), (8, 8, 12))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    r, g, b = theme["overlay"]
    for y in range(H):
        a = int(theme["min_a"] + (theme["max_a"] - theme["min_a"]) * (y / H))
        d.line([(0, y), (W, y)], fill=(r, g, b, a))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    # 頂部金色線
    draw.rectangle([0, 0, W, 10], fill=accent)

    # 帳號 / 頻道名
    font_tag = get_font(30)
    channel_name = theme["name"] + "大小事"
    draw.text((60, 40), channel_name, fill=accent, font=font_tag)

    # 日期
    date_str = datetime.now().strftime("%Y.%m.%d")
    draw.text((60, 82), date_str, fill=(120, 120, 120), font=get_font(26))

    # 中央裝飾大框
    box_y = 320
    draw.rectangle([60, box_y, W - 60, box_y + 8], fill=(*accent, 80))

    # 問題主文（大字置中）
    font_q = get_font(72)
    q_lines = textwrap.wrap(question, width=10)
    y = 420
    for line in q_lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_q)
        lw = bbox[2] - bbox[0]
        draw.text(((W - lw) // 2 + 2, y + 2), line, fill=(0, 0, 0), font=font_q)
        draw.text(((W - lw) // 2, y), line, fill=(255, 255, 255), font=font_q)
        y += 90

    # 金色裝飾線
    draw.rectangle([(W // 2) - 80, y + 20, (W // 2) + 80, y + 24], fill=accent)

    # 提示文字
    hint = "✋ 投票告訴我！"
    font_hint = get_font(34)
    hint_bbox = draw.textbbox((0, 0), hint, font=font_hint)
    hw = hint_bbox[2] - hint_bbox[0]
    draw.text(((W - hw) // 2, y + 50), hint, fill=(160, 160, 160), font=font_hint)

    # 投票選項視覺預覽（兩個大方塊）
    btn_y = 860
    btn_h = 160
    margin = 60
    gap = 30
    btn_w = (W - margin * 2 - gap) // 2

    # YES 按鈕（金色）
    draw.rounded_rectangle([margin, btn_y, margin + btn_w, btn_y + btn_h],
                           radius=20, fill=(*accent, 200))
    font_btn = get_font(46)
    yes_bbox = draw.textbbox((0, 0), yes_text, font=font_btn)
    yw = yes_bbox[2] - yes_bbox[0]
    yh = yes_bbox[3] - yes_bbox[1]
    draw.text((margin + (btn_w - yw) // 2, btn_y + (btn_h - yh) // 2),
              yes_text, fill=(0, 0, 0), font=font_btn)

    # NO 按鈕（白色框）
    no_x = margin + btn_w + gap
    draw.rounded_rectangle([no_x, btn_y, no_x + btn_w, btn_y + btn_h],
                           radius=20, outline=(200, 200, 200), width=3, fill=(30, 30, 30))
    no_bbox = draw.textbbox((0, 0), no_text, font=font_btn)
    nw = no_bbox[2] - no_bbox[0]
    nh = no_bbox[3] - no_bbox[1]
    draw.text((no_x + (btn_w - nw) // 2, btn_y + (btn_h - nh) // 2),
              no_text, fill=(220, 220, 220), font=font_btn)

    # 底部金色線
    draw.rectangle([0, H - 8, W, H], fill=accent)

    bg.save(out_path, "JPEG", quality=90)
    print(f"✅ 限動底圖已生成：{out_path}")
    return out_path


def post_story(channel: str, question: str, yes_text: str, no_text: str,
               dry_run: bool = False) -> bool:
    """生成限動圖並上傳到 IG"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    story_dir = Path.home() / ".openclaw/workspace/agents/assistant-work/cards/stories"
    story_dir.mkdir(parents=True, exist_ok=True)
    story_path = str(story_dir / f"story_{channel}_{ts}.jpg")

    make_story_image(channel, question, yes_text, no_text, story_path)

    if dry_run:
        print(f"🔍 [Dry Run] 限動圖已生成，不實際發布")
        print(f"   檔案：{story_path}")
        print(f"   問題：{question}")
        print(f"   YES：{yes_text} | NO：{no_text}")
        return True

    ig_config_path = IG_CONFIG_MAP.get(channel, SCRIPT_DIR / "ig_config.json")
    if not ig_config_path.exists():
        print(f"❌ IG 設定檔不存在：{ig_config_path}")
        return False

    config = json.loads(ig_config_path.read_text())
    username = config.get("username", "")
    password = config.get("password", "")

    try:
        from instagrapi import Client
        from instagrapi.types import StoryPoll, StoryHashtag, StoryLink

        cl = Client()
        cl.delay_range = [1, 3]

        session_path = SCRIPT_DIR / f"ig_session_{channel}.json"
        if session_path.exists():
            try:
                cl.load_settings(session_path)
                cl.login(username, password)
                cl.get_timeline_feed()
                print(f"✅ 使用已儲存的 Session 登入：@{username}")
            except Exception:
                session_path.unlink(missing_ok=True)
                cl.login(username, password)
                cl.dump_settings(session_path)
        else:
            print(f"🔐 登入 IG：@{username}")
            cl.login(username, password)
            cl.dump_settings(session_path)
            print("✅ 登入成功")

        # 建立投票貼紙
        poll = StoryPoll(
            question=question,
            tallies=[
                {"text": yes_text, "font_size": 28.0, "count": 0, "is_selected": False},
                {"text": no_text,  "font_size": 28.0, "count": 0, "is_selected": False},
            ],
            x=0.5,    # 水平置中（0-1）
            y=0.65,   # 垂直位置（0-1，約在圖的 65% 處）
            width=0.7,
            height=0.14,
            rotation=0.0,
        )

        print(f"📤 上傳限動（含投票）...")
        story = cl.story_upload(
            path=story_path,
            caption="",
            polls=[poll],
        )
        print(f"✅ 限動發布成功！")
        print(f"   Story ID：{story.id}")
        return True

    except ImportError:
        print("❌ instagrapi 未安裝：pip install instagrapi")
        return False
    except Exception as e:
        print(f"❌ 限動發布失敗：{e}")
        import traceback; traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IG 自動限動 + 投票")
    parser.add_argument("--channel", choices=["crypto", "finance", "startup"],
                        default="crypto")
    parser.add_argument("--question", default="", help="自訂投票問題（預設自動）")
    parser.add_argument("--yes", default="", help="YES 選項文字")
    parser.add_argument("--no", default="", help="NO 選項文字")
    parser.add_argument("--dry-run", action="store_true", help="只生成圖，不發布")
    args = parser.parse_args()

    # 如果沒指定，用今日自動輪換
    if args.question:
        poll_data = {"question": args.question,
                     "yes": args.yes or "✅ 是",
                     "no": args.no or "❌ 否"}
    else:
        poll_data = get_poll_for_today(args.channel)
        print(f"📅 今日投票：{poll_data['question']}")

    success = post_story(
        args.channel,
        poll_data["question"],
        poll_data["yes"],
        poll_data["no"],
        dry_run=args.dry_run,
    )
    sys.exit(0 if success else 1)
