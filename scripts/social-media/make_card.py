#!/usr/bin/env python3
"""
IG 圖卡生成器 v4 — 全頁照片背景 + 5 張 Carousel
風格：
  crypto/finance → 參考 @abmedia_io（財經黑金色，大字震撼，整頁照片感）
  startup        → 參考 @the_insight_circle（極簡黑白，高端雜誌感）

v4 改版：
  - 每張 Slide 不同裁切偏移（背景有變化）
  - 移除底部黑條（整頁感更強，更像鏈新聞）
  - 內容更深更多（三大重點各有標題+說明）
  - 移除來源文字
  - 滑動提示顏色加亮
"""

import argparse
import os
import sys
import json
import math
import random
import re as _re
import textwrap
import hashlib
import time
from io import BytesIO
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from html.parser import HTMLParser
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


# ── 智慧斷行（不切斷英文字 / 數字 / 標點後短句）──────────────
def smart_wrap(text: str, width: int) -> list[str]:
    """中英混排智慧斷行，避免把英文單字、數字、標點後短句切斷。

    規則：
    1. 先把文字拆成 token（中文字、英文單字、數字串、標點）
    2. 中文字寬度 = 2，英數字寬度 = 1，全形標點 = 2
    3. 逐 token 填入一行，超出 width 時換行
    4. 標點符號後若只剩 ≤4 個字元到下一個標點，拉到同一行
    """
    if not text:
        return []

    # 拆 token：中文字 | 英文+數字連續 | 標點 | 空格
    tokens = _re.findall(
        r'[a-zA-Z0-9][a-zA-Z0-9.,\':\-/_%]*'  # 英數（含內嵌標點如 79,311）
        r'|[，。！？、；：…—「」『』（）《》\)\(\[\]]'  # 全形標點
        r'|[\u4e00-\u9fff\u3400-\u4dbf]'          # 中文字
        r'|\s+'                                     # 空格
        r'|.',                                      # 其他
        text
    )

    # ── 合併括號對：把 「...」『...』（...）《...》 視為一個不可分割的 token ──
    # 但如果括號內容太長（超過 80% 行寬），就不合併，避免溢出
    _OPEN_CLOSE = {'「': '」', '『': '』', '（': '）', '《': '》', '(': ')', '[': ']'}

    def _tok_w_quick(t: str) -> int:
        """快速估算 token 寬度（用於合併前判斷）"""
        w = 0
        for c in t:
            if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf':
                w += 2
            elif c in '，。！？、；：…—「」（）《》':
                w += 2
            else:
                w += 1
        return w

    merged_tokens = []
    ti = 0
    while ti < len(tokens):
        if tokens[ti] in _OPEN_CLOSE:
            close_ch = _OPEN_CLOSE[tokens[ti]]
            group = [tokens[ti]]
            ti += 1
            while ti < len(tokens) and tokens[ti] != close_ch:
                group.append(tokens[ti])
                ti += 1
            if ti < len(tokens):  # 找到閉括號
                group.append(tokens[ti])
                ti += 1
            # 合併前檢查：太長的括號內容不合併，維持原始 token 讓逐字斷行
            merged_token = ''.join(group)
            if _tok_w_quick(merged_token) > width * 2 * 0.8:
                merged_tokens.extend(group)
            else:
                merged_tokens.append(merged_token)
        else:
            merged_tokens.append(tokens[ti])
            ti += 1
    tokens = merged_tokens

    def tok_w(t: str) -> int:
        """估算 token 的等寬字數（中文=2, 英數=1, 全形標點=2）"""
        w = 0
        for c in t:
            if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf':
                w += 2
            elif c in '，。！？、；：…—「」（）《》':
                w += 2
            else:
                w += 1
        return w

    lines = []
    cur_tokens: list[str] = []
    cur_w = 0

    for tok in tokens:
        tw_ = tok_w(tok)
        # 空格 token 在行首跳過
        if tok.isspace() and cur_w == 0:
            continue
        # 如果加上這個 token 會超過寬度
        if cur_w + tw_ > width * 2 and cur_tokens:
            # 標點不應該出現在下一行開頭 → 留在這行
            if tok in '，。！？、；：…—）」》':
                cur_tokens.append(tok)
                cur_w += tw_
                lines.append(''.join(cur_tokens))
                cur_tokens = []
                cur_w = 0
                continue
            # 結束這行
            lines.append(''.join(cur_tokens))
            cur_tokens = [tok] if not tok.isspace() else []
            cur_w = 0 if tok.isspace() else tw_
        else:
            cur_tokens.append(tok)
            cur_w += tw_

    if cur_tokens:
        lines.append(''.join(cur_tokens))

    # 後處理：短尾併入上一行（避免「美元高點。」單獨一行）
    merged = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if merged and len(stripped) <= 6:
            # 計算併入後的寬度
            merged_w = sum(2 if ('\u4e00' <= c <= '\u9fff' or c in '，。！？、；：…—「」（）《》')
                          else 1 for c in merged[-1] + stripped)
            if merged_w <= width * 2 + 14:
                merged[-1] += stripped
                continue
        merged.append(line)

    return merged


def _wrap_to_pixels(draw, text: str, font, max_width_px: int) -> list[str]:
    """Wrap text so each line's ACTUAL rendered width fits within max_width_px.

    Uses draw.textlength (Pillow) for real pixel measurements — avoids the
    weighted-unit mismatch in smart_wrap that can cause 880px text to be
    claimed as "fitting" in a 779px box.
    """
    if not text:
        return []

    def _measure(s: str) -> float:
        try:
            return draw.textlength(s, font=font)
        except AttributeError:
            bbox = draw.textbbox((0, 0), s, font=font)
            return bbox[2] - bbox[0]

    tokens = _re.findall(
        r'[a-zA-Z0-9][a-zA-Z0-9.,\':\-/_%]*'
        r'|[，。！？、；：…—「」『』（）《》\)\(\[\]]'
        r'|[\u4e00-\u9fff\u3400-\u4dbf]'
        r'|\s+'
        r'|.',
        text
    )

    lines: list[str] = []
    cur = ""
    for tok in tokens:
        if tok.isspace() and not cur:
            continue
        candidate = cur + tok
        if _measure(candidate) <= max_width_px:
            cur = candidate
            continue
        # Overflow: break punctuation-aware
        if tok in '，。！？、；：…—）」》' and cur:
            # keep punctuation with current line even if slight overflow
            lines.append(cur + tok)
            cur = ""
            continue
        if cur:
            lines.append(cur)
        cur = "" if tok.isspace() else tok
    if cur:
        lines.append(cur)
    return lines


# ── 字體 ─────────────────────────────────────────────────────
FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

# ── 真實走勢圖（CoinGecko API + matplotlib）──────────────────
def _smooth_data(vals: list, window: int = 5) -> list:
    """簡單移動平均平滑數據，保留首尾真實值"""
    if len(vals) <= window:
        return vals
    smoothed = list(vals)  # 不改原始 list
    half = window // 2
    for i in range(half, len(vals) - half):
        smoothed[i] = sum(vals[i - half:i + half + 1]) / window
    return smoothed


def _downsample(times: list, vals: list, target: int = 200) -> tuple:
    """降低數據點數到 target，保留首尾和高低點"""
    if len(vals) <= target:
        return times, vals
    step = max(1, len(vals) // target)
    max_i = vals.index(max(vals))
    min_i = vals.index(min(vals))
    # 取等距點 + 確保高低點被保留
    keep = set(range(0, len(vals), step))
    keep.add(0)
    keep.add(len(vals) - 1)
    keep.add(max_i)
    keep.add(min_i)
    indices = sorted(keep)
    return [times[i] for i in indices], [vals[i] for i in indices]


# ── mplfinance K 線圖支援 ────────────────────────────────────

def _fetch_ohlcv_yahoo(symbol: str, days: int = 7) -> dict:
    """從 Yahoo Finance 取得 OHLCV 資料（開高低收量）。
    返回 {'timestamps', 'opens', 'highs', 'lows', 'closes', 'volumes'}
    或空 dict 表示失敗。"""
    try:
        import json as _json
        from urllib.request import urlopen as _urlopen, Request as _Req
        from urllib.parse import quote as _quote

        range_map = {1: "1d", 7: "5d", 30: "1mo", 90: "3mo"}
        interval_map = {1: "5m", 7: "1h", 30: "1d", 90: "1d"}
        yf_range = range_map.get(days, "5d")
        yf_interval = interval_map.get(days, "1h")

        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{_quote(symbol)}"
               f"?range={yf_range}&interval={yf_interval}")
        req = _Req(url, headers={"User-Agent": "Mozilla/5.0"})
        data = _json.loads(_urlopen(req, timeout=15).read())
        result = data["chart"]["result"][0]

        ts = result["timestamp"]
        q = result["indicators"]["quote"][0]
        opens   = q.get("open",   [])
        highs   = q.get("high",   [])
        lows    = q.get("low",    [])
        closes  = q.get("close",  [])
        volumes = q.get("volume", [])

        # 過濾 None 值（保持各列同步）
        valid = [
            (t, o, h, l, c, v)
            for t, o, h, l, c, v in zip(ts, opens, highs, lows, closes, volumes)
            if all(x is not None for x in (o, h, l, c))
        ]
        if len(valid) < 5:
            return {}

        return {
            "timestamps": [r[0] for r in valid],
            "opens":      [r[1] for r in valid],
            "highs":      [r[2] for r in valid],
            "lows":       [r[3] for r in valid],
            "closes":     [r[4] for r in valid],
            "volumes":    [r[5] if r[5] is not None else 0 for r in valid],
        }
    except Exception:
        return {}


def _render_candlestick_mplfinance(ohlcv: dict, label: str,
                                   size: tuple, days: int) -> tuple:
    """用 mplfinance 渲染 K 線蠟燭圖 + 成交量柱狀圖，轉為 PIL Image。
    需要：mplfinance, pandas, matplotlib（安裝任一缺失則返回 (None, {})）。
    """
    try:
        import mplfinance as mpf
        import pandas as pd
        from datetime import datetime as _dt
        from io import BytesIO as _BytesIO

        timestamps = [_dt.fromtimestamp(t) for t in ohlcv["timestamps"]]
        df = pd.DataFrame({
            "Open":   ohlcv["opens"],
            "High":   ohlcv["highs"],
            "Low":    ohlcv["lows"],
            "Close":  ohlcv["closes"],
            "Volume": ohlcv["volumes"],
        }, index=pd.DatetimeIndex(timestamps))

        closes = ohlcv["closes"]
        change = closes[-1] - closes[0]
        pct = change / closes[0] * 100 if closes[0] != 0 else 0
        is_up = change >= 0
        arrow = "▲" if is_up else "▼"

        up_color   = "#4ade80"
        down_color = "#f87171"

        mc = mpf.make_marketcolors(
            up=up_color, down=down_color,
            wick={"up": up_color, "down": down_color},
            volume={"up": up_color, "down": down_color},
            ohlc={"up": up_color, "down": down_color},
        )
        s = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            marketcolors=mc,
            facecolor="#12121a",
            figcolor="#12121a",
            gridcolor="#ffffff15",
            gridstyle=":",
        )

        W, H = size
        dpi = 100
        fig_w = W / dpi
        fig_h = H / dpi

        fig, _ = mpf.plot(
            df,
            type="candle",
            volume=True,
            returnfig=True,
            style=s,
            figsize=(fig_w, fig_h),
            show_nontrading=False,
            tight_layout=True,
        )

        buf = _BytesIO()
        fig.savefig(buf, format="png", dpi=dpi,
                    bbox_inches="tight", facecolor="#12121a")
        buf.seek(0)

        import matplotlib.pyplot as _plt
        _plt.close(fig)

        candle_img = Image.open(buf).convert("RGBA")
        candle_img = candle_img.resize(size, Image.Resampling.LANCZOS)

        print(f"   📊 K 線圖（mplfinance）：{label} ${closes[-1]:,.2f} ({pct:+.1f}%)")
        meta = {
            "pct": pct, "current": closes[-1], "coin": label,
            "arrow": arrow, "is_up": is_up,
            "high": max(ohlcv["highs"]), "low": min(ohlcv["lows"]),
        }
        return candle_img, meta

    except ImportError:
        return None, {}
    except Exception as e:
        print(f"   ⚠️ mplfinance K 線圖失敗：{e}")
        return None, {}


def fetch_price_chart(coin: str = "bitcoin", days: int = 7,
                      size: tuple = (960, 500)) -> tuple[Optional[Image.Image], dict]:
    """用 Pillow 直接繪製極簡漸層面積走勢圖（不依賴 matplotlib）。
    風格：CoinMarketCap app — 粗線 + 漸層填色，無座標軸，只標高低現價。"""
    try:
        import json as _json
        from urllib.request import urlopen as _urlopen, Request as _Req
        from datetime import datetime as _dt

        url = (f"https://api.coingecko.com/api/v3/coins/{coin}/"
               f"market_chart?vs_currency=usd&days={days}")
        req = _Req(url, headers={"User-Agent": "Mozilla/5.0",
                                  "Accept": "application/json"})
        data = _json.loads(_urlopen(req, timeout=15).read())
        prices = data["prices"]

        vals_raw = [p[1] for p in prices]
        change = vals_raw[-1] - vals_raw[0]
        pct = change / vals_raw[0] * 100
        is_up = change >= 0
        arrow = "▲" if is_up else "▼"
        _COIN_LABELS = {
            "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL",
            "binancecoin": "BNB", "ripple": "XRP", "cardano": "ADA",
            "dogecoin": "DOGE", "polkadot": "DOT", "avalanche-2": "AVAX",
            "matic-network": "MATIC", "chainlink": "LINK",
            "sui": "SUI", "the-open-network": "TON",
        }
        coin_label = _COIN_LABELS.get(coin, coin.upper()[:5])

        # 降採樣 + 平滑
        times_raw = [_dt.fromtimestamp(p[0] / 1000) for p in prices]
        _, vals_ds = _downsample(times_raw, vals_raw, target=120)
        window = 5 if days >= 7 else 3
        vals = _smooth_data(vals_ds, window=window)

        W, H = size
        # 繪圖區域（留邊距）
        pad_l, pad_r, pad_t, pad_b = 10, 10, 10, 10
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b

        v_min, v_max = min(vals), max(vals)
        v_range = v_max - v_min if v_max > v_min else 1
        # y 軸留 10% 空間
        v_min_plot = v_min - v_range * 0.08
        v_max_plot = v_max + v_range * 0.08
        v_range_plot = v_max_plot - v_min_plot

        def _val_to_y(v: float) -> int:
            return pad_t + int((1 - (v - v_min_plot) / v_range_plot) * ch)

        def _idx_to_x(i: int) -> int:
            return pad_l + int(i / max(len(vals) - 1, 1) * cw)

        # 算出折線點
        points = [(_idx_to_x(i), _val_to_y(v)) for i, v in enumerate(vals)]

        # 線條顏色
        line_rgb = (74, 222, 128) if is_up else (248, 113, 113)  # 綠漲紅跌
        grad_top = (*line_rgb, 80)  # 漸層頂部（半透明）
        grad_bot = (*line_rgb, 0)   # 漸層底部（全透明）

        # 底圖（透明）
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        # ── 1. 漸層填色區（線下方到底部）──
        # 用逐行掃描填色
        bottom_y = pad_t + ch
        grad_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(grad_layer)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            # 對這段 x 範圍，從線到底部填漸層
            for x in range(x1, x2 + 1):
                if x2 == x1:
                    t = 0
                else:
                    t = (x - x1) / (x2 - x1)
                line_y = int(y1 + t * (y2 - y1))
                for y in range(line_y, bottom_y):
                    # 漸層 alpha：離線越遠越透明
                    frac = (y - line_y) / max(bottom_y - line_y, 1)
                    a = int(grad_top[3] * (1 - frac) + grad_bot[3] * frac)
                    if a > 0:
                        grad_draw.point((x, y), fill=(*line_rgb, a))

        img = Image.alpha_composite(img, grad_layer)
        draw = ImageDraw.Draw(img)

        # ── 2. 主線條（粗 4px，用多次偏移模擬）──
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 5:  # 圓形筆刷
                    shifted = [(x + dx, y + dy) for x, y in points]
                    draw.line(shifted, fill=(*line_rgb, 255), width=1)

        # ── 3. 高點標記 ──
        max_i = vals.index(max(vals))
        mx, my = points[max_i]
        # 光暈
        for r in range(12, 3, -1):
            a = int(40 * (1 - r / 12))
            draw.ellipse([mx - r, my - r, mx + r, my + r],
                         fill=(247, 183, 49, a))
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5],
                     fill=(247, 183, 49, 255))
        # 標籤
        hi_font = get_font(22)
        hi_text = f"${v_max:,.0f}"
        hi_y = my - 32 if my > pad_t + 40 else my + 16
        draw_shadow_text(draw, (mx + 12, hi_y), hi_text, hi_font,
                         fill=(247, 183, 49), offset=2)

        # ── 4. 低點標記 ──
        min_i = vals.index(min(vals))
        nx, ny = points[min_i]
        for r in range(12, 3, -1):
            a = int(40 * (1 - r / 12))
            draw.ellipse([nx - r, ny - r, nx + r, ny + r],
                         fill=(248, 113, 113, a))
        draw.ellipse([nx - 5, ny - 5, nx + 5, ny + 5],
                     fill=(248, 113, 113, 255))
        lo_font = get_font(22)
        lo_text = f"${v_min:,.0f}"
        lo_y = ny + 12 if ny < pad_t + ch - 40 else ny - 32
        draw_shadow_text(draw, (nx + 12, lo_y), lo_text, lo_font,
                         fill=(248, 113, 113), offset=2)

        # ── 5. 現價終點 ──
        ex, ey = points[-1]
        draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6],
                     fill=(255, 255, 255, 255), outline=(*line_rgb, 255), width=2)

        print(f"   📈 走勢圖生成：{coin_label} ${vals_raw[-1]:,.0f} ({pct:+.1f}%)")
        chart_meta = {"pct": pct, "current": vals_raw[-1], "coin": coin_label,
                      "arrow": arrow, "is_up": is_up,
                      "high": v_max, "low": v_min}
        return img, chart_meta
    except Exception as e:
        print(f"   ⚠️ 走勢圖生成失敗：{e}")
        return None, {}


def fetch_commodity_chart(symbol: str = "GC=F", label: str = "黃金",
                          days: int = 7,
                          size: tuple = (960, 500)) -> tuple[Optional[Image.Image], dict]:
    """用 Yahoo Finance API 取得商品/個股走勢。
    優先嘗試 mplfinance K 線蠟燭圖（需安裝 mplfinance + pandas），
    否則 fallback 到 Pillow 極簡漸層面積圖。
    支援黃金(GC=F)、白銀(SI=F)、原油(CL=F)、個股(TSLA 等) 等。"""

    # 優先嘗試 mplfinance K 線圖（更專業、更好看）
    _ohlcv = _fetch_ohlcv_yahoo(symbol, days)
    if _ohlcv:
        _mpf_img, _mpf_meta = _render_candlestick_mplfinance(_ohlcv, label, size, days)
        if _mpf_img is not None:
            return _mpf_img, _mpf_meta

    # Fallback：Pillow 漸層面積圖
    try:
        import json as _json
        from urllib.request import urlopen as _urlopen, Request as _Req
        from urllib.parse import quote as _quote

        range_map = {1: "1d", 7: "5d", 30: "1mo", 90: "3mo"}
        interval_map = {1: "5m", 7: "1h", 30: "1d", 90: "1d"}
        yf_range = range_map.get(days, "5d")
        yf_interval = interval_map.get(days, "1h")

        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{_quote(symbol)}"
               f"?range={yf_range}&interval={yf_interval}")
        req = _Req(url, headers={"User-Agent": "Mozilla/5.0"})
        data = _json.loads(_urlopen(req, timeout=15).read())
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]

        # 過濾 None 值
        valid = [(t, c) for t, c in zip(timestamps, closes) if c is not None]
        if len(valid) < 5:
            return None, {}

        vals_raw = [c for _, c in valid]
        change = vals_raw[-1] - vals_raw[0]
        pct = change / vals_raw[0] * 100
        is_up = change >= 0
        arrow = "▲" if is_up else "▼"

        from datetime import datetime as _dt
        times_raw = [_dt.fromtimestamp(t) for t, _ in valid]
        _, vals_ds = _downsample(times_raw, vals_raw, target=120)
        window = 5 if days >= 7 else 3
        vals = _smooth_data(vals_ds, window=window)

        W, H = size
        pad_l, pad_r, pad_t, pad_b = 10, 10, 10, 10
        cw = W - pad_l - pad_r
        ch = H - pad_t - pad_b

        v_min, v_max = min(vals), max(vals)
        v_range = v_max - v_min if v_max > v_min else 1
        v_min_plot = v_min - v_range * 0.08
        v_max_plot = v_max + v_range * 0.08
        v_range_plot = v_max_plot - v_min_plot

        def _val_to_y(v: float) -> int:
            return pad_t + int((1 - (v - v_min_plot) / v_range_plot) * ch)

        def _idx_to_x(i: int) -> int:
            return pad_l + int(i / max(len(vals) - 1, 1) * cw)

        points = [(_idx_to_x(i), _val_to_y(v)) for i, v in enumerate(vals)]

        line_rgb = (74, 222, 128) if is_up else (248, 113, 113)
        grad_top = (*line_rgb, 80)
        grad_bot = (*line_rgb, 0)

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bottom_y = pad_t + ch
        grad_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(grad_layer)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            for x in range(x1, x2 + 1):
                t = 0 if x2 == x1 else (x - x1) / (x2 - x1)
                line_y = int(y1 + t * (y2 - y1))
                for y in range(line_y, bottom_y):
                    frac = (y - line_y) / max(bottom_y - line_y, 1)
                    a = int(grad_top[3] * (1 - frac) + grad_bot[3] * frac)
                    if a > 0:
                        grad_draw.point((x, y), fill=(*line_rgb, a))

        img = Image.alpha_composite(img, grad_layer)
        draw = ImageDraw.Draw(img)

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 5:
                    shifted = [(x + dx, y + dy) for x, y in points]
                    draw.line(shifted, fill=(*line_rgb, 255), width=1)

        max_i = vals.index(max(vals))
        mx, my = points[max_i]
        for r in range(12, 3, -1):
            a = int(40 * (1 - r / 12))
            draw.ellipse([mx - r, my - r, mx + r, my + r],
                         fill=(247, 183, 49, a))
        draw.ellipse([mx - 5, my - 5, mx + 5, my + 5],
                     fill=(247, 183, 49, 255))
        hi_font = get_font(22)
        hi_text = f"${v_max:,.0f}"
        hi_y = my - 32 if my > pad_t + 40 else my + 16
        draw_shadow_text(draw, (mx + 12, hi_y), hi_text, hi_font,
                         fill=(247, 183, 49), offset=2)

        min_i = vals.index(min(vals))
        nx, ny = points[min_i]
        for r in range(12, 3, -1):
            a = int(40 * (1 - r / 12))
            draw.ellipse([nx - r, ny - r, nx + r, ny + r],
                         fill=(248, 113, 113, a))
        draw.ellipse([nx - 5, ny - 5, nx + 5, ny + 5],
                     fill=(248, 113, 113, 255))
        lo_font = get_font(22)
        lo_text = f"${v_min:,.0f}"
        lo_y = ny + 12 if ny < pad_t + ch - 40 else ny - 32
        draw_shadow_text(draw, (nx + 12, lo_y), lo_text, lo_font,
                         fill=(248, 113, 113), offset=2)

        ex, ey = points[-1]
        draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6],
                     fill=(255, 255, 255, 255), outline=(*line_rgb, 255), width=2)

        print(f"   📈 走勢圖生成：{label} ${vals_raw[-1]:,.0f} ({pct:+.1f}%)")
        chart_meta = {"pct": pct, "current": vals_raw[-1], "coin": label,
                      "arrow": arrow, "is_up": is_up,
                      "high": v_max, "low": v_min}
        return img, chart_meta
    except Exception as e:
        print(f"   ⚠️ 商品走勢圖生成失敗：{e}")
        return None, {}


# ── 帳號設定 ──────────────────────────────────────────────────
IG_ACCOUNTS = {
    "crypto":  "money.showtime",
    "finance": "money.showtime",
    "startup": "bossmaker.lab",
}

# ── 頻道 Logo 圖檔 ───────────────────────────────────────────
LOGO_DIR = Path(__file__).parent / "assets"
CHANNEL_LOGOS = {
    "crypto":  LOGO_DIR / "logo_money_showtime.png",
    "finance": LOGO_DIR / "logo_money_showtime.png",
    "startup": LOGO_DIR / "logo_bossmaker_lab.png",
}

# ── 輪替色彩主題（theme-factory 生成，每篇文章不同配色）─────────
THEME_PALETTES = [
    {   # 0: Cyber Gold（經典比特幣金）
        "accent": (247, 183, 49),
        "grad_start": (10, 8, 20), "grad_end": (30, 22, 5),
        "highlight": (255, 215, 0), "glow": (247, 183, 49),
    },
    {   # 1: Neon Cyan（科技冷光）
        "accent": (0, 230, 255),
        "grad_start": (5, 10, 25), "grad_end": (0, 20, 35),
        "highlight": (100, 255, 255), "glow": (0, 180, 220),
    },
    {   # 2: Violet Pulse（以太紫）
        "accent": (160, 100, 255),
        "grad_start": (15, 5, 30), "grad_end": (25, 10, 45),
        "highlight": (200, 160, 255), "glow": (130, 80, 220),
    },
    {   # 3: Emerald Chain（鏈綠）
        "accent": (0, 220, 130),
        "grad_start": (5, 18, 12), "grad_end": (0, 30, 20),
        "highlight": (100, 255, 180), "glow": (0, 200, 120),
    },
    {   # 4: Solar Flare（烈焰橘）
        "accent": (255, 120, 30),
        "grad_start": (20, 8, 2), "grad_end": (35, 15, 5),
        "highlight": (255, 180, 80), "glow": (255, 100, 20),
    },
    {   # 5: Arctic Blue（冰藍）
        "accent": (70, 140, 255),
        "grad_start": (5, 8, 22), "grad_end": (10, 18, 40),
        "highlight": (140, 190, 255), "glow": (60, 120, 230),
    },
    {   # 6: Rose Gold（玫瑰金）
        "accent": (230, 150, 130),
        "grad_start": (22, 10, 12), "grad_end": (35, 18, 20),
        "highlight": (255, 200, 185), "glow": (210, 130, 110),
    },
    {   # 7: Midnight Galaxy（深紫宇宙）
        "accent": (170, 130, 255),
        "grad_start": (12, 8, 28), "grad_end": (20, 12, 50),
        "highlight": (210, 180, 255), "glow": (140, 100, 230),
    },
]


def _pick_palette(seed_text: str) -> dict:
    """根據文章內容 hash 選擇一個配色，確保每篇文章不同色系"""
    idx = abs(hash(seed_text)) % len(THEME_PALETTES)
    return THEME_PALETTES[idx]


# ── 程式化生成背景（algorithmic-art 風格）───────────────────────

def _gen_bg_grid(W: int, H: int, palette: dict, seed: int) -> Image.Image:
    """幾何網格 + 漸層：細線交叉網格 + 角落光暈"""
    r = _seeded_random(seed)
    gs, ge = palette["grad_start"], palette["grad_end"]
    glow = palette["glow"]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # 漸層底色
    for y in range(H):
        t = y / H
        c = tuple(int(gs[i] + (ge[i] - gs[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # 細線網格
    spacing = 60 + int(r() * 40)
    line_color = (*glow, 15)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, W, spacing):
        offset = int(r() * 20 - 10)
        od.line([(x + offset, 0), (x, H)], fill=line_color, width=1)
    for y in range(0, H, spacing):
        offset = int(r() * 20 - 10)
        od.line([(0, y + offset), (W, y)], fill=line_color, width=1)
    # 角落光暈
    cx_, cy_ = int(W * (0.2 + r() * 0.6)), int(H * (0.1 + r() * 0.3))
    for radius in range(300, 0, -3):
        a = int(12 * (radius / 300))
        od.ellipse([cx_ - radius, cy_ - radius, cx_ + radius, cy_ + radius],
                   fill=(*glow, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _gen_bg_circles(W: int, H: int, palette: dict, seed: int) -> Image.Image:
    """同心環 + 粒子散佈"""
    r = _seeded_random(seed)
    gs, ge = palette["grad_start"], palette["grad_end"]
    glow = palette["glow"]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(gs[i] + (ge[i] - gs[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # 同心環
    cx_, cy_ = int(W * (0.3 + r() * 0.4)), int(H * (0.3 + r() * 0.4))
    for i in range(8):
        radius = 80 + i * 70 + int(r() * 30)
        a = max(5, 25 - i * 3)
        od.ellipse([cx_ - radius, cy_ - radius, cx_ + radius, cy_ + radius],
                   outline=(*glow, a), width=2)
    # 小粒子
    for _ in range(40):
        px, py = int(r() * W), int(r() * H)
        size = 1 + int(r() * 3)
        a = 20 + int(r() * 40)
        od.ellipse([px, py, px + size, py + size], fill=(*glow, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _gen_bg_waves(W: int, H: int, palette: dict, seed: int) -> Image.Image:
    """正弦波流場背景"""
    r = _seeded_random(seed)
    gs, ge = palette["grad_start"], palette["grad_end"]
    glow = palette["glow"]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(gs[i] + (ge[i] - gs[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    n_waves = 5 + int(r() * 4)
    for w in range(n_waves):
        freq = 0.005 + r() * 0.01
        amp = 30 + r() * 80
        phase = r() * math.pi * 2
        base_y = int(H * (0.1 + 0.8 * w / n_waves))
        a = max(8, 22 - w * 2)
        points = []
        for x in range(0, W, 3):
            y = base_y + int(amp * math.sin(freq * x + phase))
            points.append((x, y))
        if len(points) > 1:
            od.line(points, fill=(*glow, a), width=2)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _gen_bg_diamonds(W: int, H: int, palette: dict, seed: int) -> Image.Image:
    """菱形晶格背景"""
    r = _seeded_random(seed)
    gs, ge = palette["grad_start"], palette["grad_end"]
    glow = palette["glow"]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(gs[i] + (ge[i] - gs[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    size = 80 + int(r() * 40)
    for row in range(-1, H // size + 2):
        for col in range(-1, W // size + 2):
            cx_ = col * size + (size // 2 if row % 2 else 0)
            cy_ = row * size
            a = 8 + int(r() * 18)
            pts = [(cx_, cy_ - size // 2), (cx_ + size // 2, cy_),
                   (cx_, cy_ + size // 2), (cx_ - size // 2, cy_)]
            od.polygon(pts, outline=(*glow, a), fill=None)
    # 中心高光
    cx_, cy_ = W // 2 + int(r() * 200 - 100), H // 3 + int(r() * 100)
    for radius in range(250, 0, -5):
        a = int(8 * (radius / 250))
        od.ellipse([cx_ - radius, cy_ - radius, cx_ + radius, cy_ + radius],
                   fill=(*glow, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


_BG_GENERATORS = [_gen_bg_grid, _gen_bg_circles, _gen_bg_waves, _gen_bg_diamonds]


def _seeded_random(seed: int):
    """簡易確定性隨機數產生器（不需 import random）"""
    state = [seed & 0xFFFFFFFF]
    def _next():
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return state[0] / 0x7FFFFFFF
    return _next


def generate_art_background(W: int, H: int, palette: dict,
                            slide_idx: int = 0, article_seed: str = "") -> Image.Image:
    """為每張 slide 生成獨特的程式化背景（每張 slide 不同圖案 + 不同隨機種子）"""
    seed = abs(hash(f"{article_seed}-{slide_idx}")) & 0xFFFFFFFF
    gen_idx = (slide_idx + abs(hash(article_seed))) % len(_BG_GENERATORS)
    gen = _BG_GENERATORS[gen_idx]
    return gen(W, H, palette, seed)


# ── 頻道主題 ──────────────────────────────────────────────────
THEMES = {
    "crypto": {
        "name": "幣圈大小事",
        "name_en": "CRYPTO NEWS",
        "ig": "money.showtime",
        "accent": (247, 183, 49),     # Bitcoin gold — brand signature color
        "overlay": (0, 0, 0),
        "overlay_min_alpha": 100,
        "overlay_max_alpha": 220,
        "keyword": "bitcoin cryptocurrency blockchain trading",
        "emoji": "₿",
        "style": "abmedia",
        "bg_color": (13, 13, 13),
        "card_bg": (255, 255, 255, 15),
    },
    "finance": {
        "name": "金融大小事",
        "name_en": "FINANCE NEWS",
        "ig": "money.showtime",
        "accent": (247, 183, 49),
        "overlay": (0, 5, 15),
        "overlay_min_alpha": 100,
        "overlay_max_alpha": 220,
        "keyword": "stock market finance wall street trading",
        "emoji": "📈",
        "style": "abmedia",
        "bg_color": (13, 13, 13),
        "card_bg": (255, 255, 255, 15),
    },
    "startup": {
        "name": "創業大小事",
        "name_en": "STARTUP STORIES",
        "ig": "bossmaker.lab",
        "accent": (220, 175, 105),
        "overlay": (5, 5, 8),
        "overlay_min_alpha": 130,
        "overlay_max_alpha": 240,
        "keyword": "entrepreneur startup business office success",
        "emoji": "💡",
        "style": "abmedia",
        "bg_color": (13, 13, 13),
        "card_bg": (255, 255, 255, 15),
    },
}

# 每張 Slide 各自獨立的圖片搜尋關鍵字（4-6 頁版：Cover + KeyPoints + FAQ/Analysis + Ending）
SLIDE_COUNT = 4  # Default: Cover + KeyPoints + FAQ/Analysis + Ending (can grow to 6)
SLIDE_PHOTO_KEYWORDS = {
    "crypto": [
        None,                                   # 1: Cover (AI/photo)
        "cryptocurrency,market,blockchain",     # 2: Key Points
        "bitcoin,finance,analysis",             # 3: FAQ/Analysis
        None,                                   # 4: Ending (solid bg)
    ],
    "finance": [
        None,
        "stock,market,finance",
        "economy,global,business",
        None,
    ],
    "startup": [
        None,
        "startup,innovation,technology",
        "entrepreneur,business,venture",
        None,
    ],
}

# 裁切偏移（每張 slide 不同偏移，確保背景多樣性，最多 6 張）
SLIDE_CROPS = [
    (0,    0),
    (80,   40),
    (-80,  40),
    (40,  -60),
    (-40,  80),
    (60,   -80),
]


# ── 工具函式 ──────────────────────────────────────────────────

def get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def tw(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    except AttributeError:
        w, _ = draw.textsize(text, font=font)
        return w


def cx(draw: ImageDraw.ImageDraw, text: str, font, W: int) -> int:
    return (W - tw(draw, text, font)) // 2


def clamp_line(draw: ImageDraw.ImageDraw, line: str, font, max_px: int) -> str:
    """如果渲染後文字寬度超過 max_px，截斷並加 '…'"""
    if tw(draw, line, font) <= max_px:
        return line
    while len(line) > 1 and tw(draw, line + "…", font) > max_px:
        line = line[:-1]
    return line + "…"


def draw_shadow_text(draw, pos, text, font, fill, shadow=(0, 0, 0), offset=3):
    """帶陰影的文字"""
    draw.text((pos[0] + offset, pos[1] + offset), text, fill=shadow, font=font)
    draw.text(pos, text, fill=fill, font=font)


def load_logo(channel: str, target_w: int = 360) -> Optional[Image.Image]:
    """載入頻道 Logo 圖片（透明背景），自動縮放到指定寬度"""
    logo_path = CHANNEL_LOGOS.get(channel)
    if not logo_path or not logo_path.exists():
        return None
    try:
        logo = Image.open(logo_path).convert("RGBA")
        ratio = target_w / logo.width
        new_h = int(logo.height * ratio)
        return logo.resize((target_w, new_h), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"   ⚠️ Logo 載入失敗：{e}")
        return None


def fit_text_params(text: str, available_h: int,
                    max_width_px: int = 880,
                    max_lines: int = 0) -> tuple[int, int, int]:
    """
    自適應文字排版：根據文字量和可用高度，計算最佳 font_size / line_h / wrap_w
    目標：填滿可用空間的 70-95%，不超出
    max_lines: 額外限制最多行數（0=不限制）
    回傳 (font_size, line_h, wrap_w)
    """
    # 候選字體設定：可讀性優先，最大只到 34px
    candidates = [
        (34, 50),
        (32, 48),
        (30, 44),
        (28, 42),
        (26, 38),
        (24, 36),
        (22, 34),
    ]
    best = (28, 42, 22)  # fallback

    for font_size, line_h in candidates:
        char_w = font_size * 0.95
        wrap_w = max(14, int(max_width_px / char_w))
        lines = smart_wrap(text, width=wrap_w)
        # 如果有 max_lines 限制，先截斷
        if max_lines > 0:
            lines = lines[:max_lines]
        total_h = len(lines) * line_h
        fill_ratio = total_h / available_h if available_h > 0 else 1

        if 0.70 <= fill_ratio <= 0.95:
            return (font_size, line_h, wrap_w)
        elif total_h <= available_h:
            best = (font_size, line_h, wrap_w)
            if fill_ratio >= 0.55:
                return best

    return best


def smart_title_lines(title: str, max_per_line: int = 11) -> list[str]:
    """標題斷行：優先在 ！？。… 等標點處自然斷行，避免單字孤立"""
    # 修復：先將字面的 \n 替換為真正的換行符
    title = title.replace("\\n", "\n")
    for punct in ['！', '？', '。', '…']:
        idx = title.find(punct)
        if 0 < idx < len(title) - 1:
            line1 = title[:idx + 1].strip()
            line2 = title[idx + 1:].strip()
            if line2:
                # 若第二段仍太長，再做一次斷行
                if len(line2) > max_per_line:
                    return [line1] + smart_wrap(line2, width=max_per_line)
                return [line1, line2]
    # 沒有標點→ 用字數斷行
    return smart_wrap(title, width=max_per_line)


def clean_preview(text: str, max_chars: int = 60) -> str:
    """截取預覽文字：在句尾（！？。）截斷，避免切到英文單字中間"""
    if len(text) <= max_chars:
        return text
    # 找最近的句尾
    for punct in ['！', '。', '？']:
        idx = text.rfind(punct, 0, max_chars + 10)
        if idx > 20:
            return text[:idx + 1]
    # 找最近的中文逗號
    idx = text.rfind('，', 0, max_chars)
    if idx > 20:
        return text[:idx]
    # 找最近的空格或ASCII標點
    idx = text.rfind(' ', 0, max_chars)
    if idx > 20:
        return text[:idx]
    return text[:max_chars]


# ── 圖片獲取 ──────────────────────────────────────────────────

class OGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.og_image = None
        self._done = False

    def handle_starttag(self, tag, attrs):
        if self._done:
            return
        if tag == "meta":
            d = dict(attrs)
            prop = d.get("property") or d.get("name") or ""
            if "og:image" in prop and d.get("content"):
                self.og_image = d["content"]
                self._done = True
        elif tag == "body":
            self._done = True


def fetch_og_image(url: str) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; IGBot/4.0)"})
        with urlopen(req, timeout=8) as r:
            html = r.read(40000).decode("utf-8", errors="ignore")
        p = OGParser()
        p.feed(html)
        return p.og_image
    except Exception as e:
        print(f"   ⚠️ OG image 失敗：{e}")
        return None


def download_image(url: str) -> Optional[Image.Image]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as r:
            data = r.read()
        return Image.open(BytesIO(data)).convert("RGB")
    except Exception as e:
        print(f"   ⚠️ 圖片下載失敗：{e}")
        return None


_og_cache: dict = {}


# ── AI 封面生成（fal-ai FLUX Pro）──────────────────────────
# 風格參考：abmedia_io (@abmedia_io) Instagram
# 核心美學：電影感 editorial photography，暗色調，人物故事感
# ★ 不用 3D CGI/黃金球/公牛——用真實攝影場景 + 戲劇性打光

# 文章情緒 → prompt 模板映射（每個情緒有多個場景變體，隨機選取避免重複）
_COVER_PROMPTS = {
    # ── 崩盤 / 暴跌 ──────────────────────────────────────────────
    "crash": [
        (   "Cinematic editorial photograph: extreme close-up of a trader's face, "
            "anxious expression, red LED ticker numbers reflected in his glasses, "
            "chaotic trading floor blurred in background, "
            "harsh side lighting, deep shadows, desaturated with red tint, "
            "film noir atmosphere, photorealistic, 85mm portrait lens look, "
            "bottom 30% fades to solid black, square 1:1"
        ),
        (   "Cinematic wide shot: empty luxury trading office at night, "
            "overturned coffee cup, single laptop screen glowing red with falling charts, "
            "venetian blind shadows across the room, rain on floor-to-ceiling windows, "
            "dark moody thriller atmosphere, teal and red color grade, "
            "bottom 30% fades to black, square 1:1, movie poster composition"
        ),
        (   "Editorial photography: crowd of people watching a massive red LED display board "
            "in a financial district plaza, faces illuminated by red glow, "
            "some covering mouths in shock, dramatic downward pointing arrows on screen, "
            "dark overcast sky, available light documentary style, "
            "bottom 30% gradually darkens to black, square format"
        ),
        (   "Cinematic close-up: single wilted red rose lying on a cracked marble floor, "
            "sharp dramatic spotlight from above, surrounding darkness, "
            "scattered banknotes and coins out of focus in background, "
            "fine art photography, melancholy atmosphere, "
            "lower 30% fades to solid black, square 1:1"
        ),
    ],
    # ── 牛市 / 看漲 ──────────────────────────────────────────────
    "bullish": [
        (   "Cinematic editorial: confident CEO or fund manager standing at floor-to-ceiling "
            "window, arms crossed, overlooking illuminated city skyline at night, "
            "green trading screens glowing behind him, rim lighting outlining his silhouette, "
            "power and authority atmosphere, deep navy and green palette, "
            "bottom 30% fades to black, square 1:1, editorial magazine cover style"
        ),
        (   "Aerial cinematic photograph: golden sunrise breaking over a major financial district, "
            "god rays piercing through skyscrapers, low morning fog in the streets, "
            "warm amber and gold color grade, expansive and triumphant mood, "
            "shot from helicopter perspective, ultra wide angle, "
            "bottom 30% fades to solid black, square format"
        ),
        (   "Editorial photography: celebration scene in dim upscale restaurant, "
            "champagne glasses raised mid-clink, bokeh city lights through large windows, "
            "warm candlelight on faces showing joy and relief, "
            "shallow depth of field, 35mm film look with slight grain, "
            "lower third darkens to black, square 1:1"
        ),
        (   "Cinematic wide shot: lone figure standing at the peak of a mountain or rooftop, "
            "arms raised in triumph, city lights sprawling below into horizon, "
            "dramatic clouds catching last light of sunset, orange and purple sky, "
            "silhouette composition, epic scale contrast, "
            "bottom 30% fades to black, square format, movie poster quality"
        ),
    ],
    # ── 監管 / 法規 ──────────────────────────────────────────────
    "regulation": [
        (   "Cinematic editorial: row of suited government officials or lawyers "
            "walking out of a grand institutional building, press cameras flashing, "
            "harsh strobe light effect, imposing neoclassical architecture columns, "
            "cold blue-grey color grade, authoritative and tense atmosphere, "
            "bottom 30% fades to black, square 1:1, documentary news photography"
        ),
        (   "Dramatic editorial photograph: heavy metal handcuffs resting on white marble desk, "
            "official documents and government seal visible, single overhead spotlight, "
            "deep surrounding shadows, cold institutional lighting, "
            "minimalist noir composition, high contrast black and white with cold tones, "
            "lower third darkens to solid black, square format"
        ),
        (   "Cinematic interior: massive empty courtroom bathed in dramatic shafts of light "
            "streaming through tall windows, judge's bench prominent and imposing, "
            "lone figure standing in vast space emphasizing scale of law, "
            "cold marble surfaces, cathedral-like grandeur, "
            "bottom 30% fades to black, square 1:1"
        ),
        (   "Editorial photography: extreme close-up of a gavel mid-strike on sound block, "
            "motion blur on impact, particles and dust in the air, "
            "dark wood textures, dramatic single-source side lighting, "
            "decisive moment capture, tense and authoritative mood, "
            "lower 30% fades to solid black, square format, cinematic crop"
        ),
    ],
    # ── ETF / 機構採用 ──────────────────────────────────────────
    "etf": [
        (   "Cinematic editorial: Bloomberg terminal in sharp focus in foreground, "
            "gold price chart showing dramatic upward movement, "
            "blurred Wall Street trading floor filled with analysts in background, "
            "professional shallow depth of field, warm office lighting, "
            "aspirational financial journalism aesthetic, "
            "bottom 30% fades to black, square 1:1"
        ),
        (   "Dramatic editorial photography: two silhouetted figures shaking hands "
            "at massive floor-to-ceiling window, city financial district at night behind them, "
            "backlit composition with warm ambient city glow, "
            "power meeting atmosphere, deep shadows inside room contrasting bright city, "
            "lower 30% darkens to solid black, square format"
        ),
        (   "Cinematic night shot: Wall Street or financial district street level, "
            "wet pavement reflections of building lights, long exposure light trails from taxis, "
            "iconic financial institution facade in background, "
            "teal and orange cinematic color grade, urban epic atmosphere, "
            "bottom 30% fades to black, square 1:1, movie poster quality"
        ),
        (   "Editorial close-up: well-dressed executive hand pressing button on trading terminal, "
            "multiple monitors with charts reflected in polished desk surface, "
            "dramatic rim lighting from screens, dark background, "
            "decisive moment, institutional confidence, professional editorial style, "
            "lower third fades to black, square format"
        ),
    ],
    # ── 駭客 / 資安事件 ──────────────────────────────────────────
    "hack": [
        (   "Cinematic thriller: lone figure in dark room, face partially illuminated "
            "by single glowing monitor, green code reflecting off their face, "
            "multiple dark screens surrounding them, heavy shadows, "
            "cyber noir atmosphere, green-tinted low-key lighting, "
            "bottom 30% fades to solid black, square 1:1, thriller movie poster style"
        ),
        (   "Editorial photography: close-up of multiple computer monitors displaying "
            "red alert warnings and error messages in dark room, "
            "panicked analyst out of focus in background, "
            "ominous red and cyan glow, tense cybersecurity incident atmosphere, "
            "documentary editorial style, high drama, "
            "lower third darkens to black, square format"
        ),
        (   "Cinematic close-up: cracked phone or laptop screen, "
            "caution warning messages glowing through the fractures, "
            "dark surrounding environment, fingers visible at edge of frame, "
            "dramatic high-contrast lighting, cool blue and red tones, "
            "fine art editorial photography, vulnerability theme, "
            "bottom 30% fades to black, square 1:1"
        ),
    ],
    # ── 空投 / 獎勵 ──────────────────────────────────────────────
    "airdrop": [
        (   "Cinematic editorial: crowd of people in urban plaza, "
            "all looking upward with expressions of surprise and delight, "
            "dramatic overhead spotlight from above, confetti or paper raining down, "
            "warm festive lighting against dark sky, candid documentary moment, "
            "bottom 30% fades to black, square 1:1"
        ),
        (   "Editorial photography: person opening mysterious envelope or box, "
            "interior golden glow reflecting on excited face, "
            "dark background, shallow depth of field, "
            "gift and reward theme, warm intimate lighting, "
            "lower third darkens to solid black, square format"
        ),
    ],
    # ── NFT / 數位藝術 ───────────────────────────────────────────
    "nft": [
        (   "Cinematic editorial: artist in dark studio, illuminated canvas or screen "
            "showing vibrant digital artwork, dramatic spotlight from above, "
            "creative chaos of tools and devices around, "
            "warm vs cool light contrast, NFT creator culture aesthetic, "
            "bottom 30% fades to black, square 1:1"
        ),
        (   "Editorial photography: luxury art auction in dim gallery, "
            "auctioneer under spotlight, bidders in shadow with numbered paddles raised, "
            "single dramatic artwork on illuminated wall, "
            "high society atmosphere, tense decisive moment, "
            "lower third darkens to solid black, square format"
        ),
    ],
    # ── 預設（綜合加密新聞）──────────────────────────────────────
    "default": [
        (   "Cinematic editorial photograph: lone business figure standing at massive "
            "floor-to-ceiling window overlooking glittering city skyline at blue hour, "
            "deep navy sky, amber city glow from below, "
            "strong rim light outlining the silhouette, pensive reflective mood, "
            "professional financial journalism aesthetic, "
            "bottom 30% fades to solid black, square 1:1, editorial magazine style"
        ),
        (   "Dramatic editorial photography: empty iconic financial district street at dawn, "
            "long shadows cast by early sun through skyscraper canyons, "
            "single figure walking in distance suggesting scale, "
            "teal and warm gold cinematic color grade, atmospheric morning mist, "
            "bottom third gradually darkens to black, square format"
        ),
        (   "Cinematic wide shot: dramatic storm clouds rolling over a major Asian city skyline "
            "at dusk, last golden light illuminating towers, dark brooding sky above, "
            "weather contrast symbolizing market uncertainty, "
            "epic landscape editorial photography, "
            "bottom 30% fades to black, square 1:1"
        ),
        (   "Editorial close-up: hands typing on keyboard in dark room, "
            "multiple monitor glow reflecting on focused analyst's face, "
            "charts and data streams visible on screens, "
            "late-night work atmosphere, teal screen glow against warm skin tones, "
            "journalistic documentary style, high concentration mood, "
            "lower 30% fades to solid black, square format, cinematic crop"
        ),
        (   "Cinematic overhead shot: circular conference table with executives in heated discussion, "
            "papers and devices spread across table, dramatic overhead lighting, "
            "Tokyo or Taipei skyline visible through glass wall behind them, "
            "power and strategy atmosphere, cool blue interior vs warm city exterior, "
            "bottom 30% fades to black, square 1:1"
        ),
    ],
}

# 隨機風格修飾語——abmedia_io editorial photography 風格
_STYLE_MODIFIERS = [
    "cinematic color grading, teal and orange LUT, film grain",
    "dramatic chiaroscuro single-source lighting, deep shadows",
    "anamorphic lens bokeh, shallow depth of field, 35mm film look",
    "desaturated editorial photography, high contrast monochrome accent",
    "moody atmospheric available light, photojournalism style",
    "blue hour ambient glow, long exposure, urban cinematic",
    "backlit rim lighting, silhouette against bright background",
    "editorial magazine cover composition, professional photojournalism",
]

# 關鍵字 → 情緒分類
_MOOD_KEYWORDS = {
    "crash": ["閃崩", "暴跌", "爆倉", "崩盤", "跳水", "插針", "清算", "跌破",
              "crash", "dump", "plunge", "liquidat", "熊市", "恐慌", "拋售", "sell-off"],
    "bullish": ["飆漲", "新高", "突破", "大漲", "狂漲", "噴發", "rally", "surge",
                "pump", "breakout", "ath", "新紀錄", "牛市", "創高", "漲停"],
    "regulation": ["監管", "sec", "法規", "禁令", "合規", "執法", "罰款",
                   "regulat", "ban", "compliance", "enforce",
                   "戰爭", "war", "制裁", "sanctions", "關稅", "tariff",
                   "地緣", "geopolit", "衝突", "conflict", "軍事", "飛彈"],
    "etf": ["etf", "基金", "機構", "吸金", "流入", "inflow", "institutional",
            "grayscale", "blackrock", "fidelity",
            "黃金", "gold", "白銀", "silver", "原油", "oil", "大宗商品", "commodity"],
    "hack": ["駭客", "被盜", "漏洞", "exploit", "hack", "stolen", "breach",
             "vulnerability"],
}


def _detect_article_mood(hook: str, what: str = "") -> str:
    """根據文章 hook 和 what 自動判斷情緒分類"""
    text = (hook + " " + what).lower()
    for mood, keywords in _MOOD_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return mood
    return "default"


# 常見加密貨幣/項目名稱 → 可用於圖片 prompt 的英文關鍵詞
_CRYPTO_NAMES = {
    "bitcoin": "Bitcoin", "btc": "Bitcoin", "比特幣": "Bitcoin",
    "ethereum": "Ethereum", "eth": "Ethereum", "以太坊": "Ethereum", "以太幣": "Ethereum",
    "solana": "Solana", "sol": "Solana",
    "xrp": "XRP", "ripple": "XRP",
    "cardano": "Cardano", "ada": "Cardano",
    "dogecoin": "Dogecoin", "doge": "Dogecoin", "狗狗幣": "Dogecoin",
    "bnb": "BNB", "binance": "Binance",
    "avalanche": "Avalanche", "avax": "Avalanche",
    "polygon": "Polygon", "matic": "Polygon",
    "polkadot": "Polkadot", "dot": "Polkadot",
    "tron": "TRON", "trx": "TRON",
    "chainlink": "Chainlink", "link": "Chainlink",
    "stablecoin": "stablecoin", "穩定幣": "stablecoin",
    "nft": "NFT", "defi": "DeFi", "dao": "DAO",
    "memecoin": "memecoin", "迷因幣": "memecoin",
}


def _extract_topic_keywords(hook: str, what: str = "") -> str:
    """從文章 hook/what 提取具體主題關鍵詞，用於讓封面圖更貼合文章內容。
    回傳一段英文描述片段（可直接嵌入 prompt），若無特定主題則回傳空字串。"""
    text = (hook + " " + what).lower()
    found = []
    for keyword, english_name in _CRYPTO_NAMES.items():
        if keyword in text and english_name not in found:
            found.append(english_name)
    if found:
        return "featuring " + " and ".join(found[:3]) + " imagery"

    # 擴展：偵測更多主題關鍵詞
    _TOPIC_MAP = {
        "ai": "artificial intelligence", "人工智慧": "artificial intelligence",
        "apple": "Apple technology", "蘋果": "Apple technology",
        "google": "Google technology", "tesla": "Tesla electric vehicles",
        "特斯拉": "Tesla", "fed": "Federal Reserve monetary policy",
        "聯準會": "Federal Reserve", "央行": "central bank monetary policy",
        "降息": "interest rate cut", "升息": "interest rate hike",
        "通膨": "inflation", "gdp": "economic growth GDP",
        "股市": "stock market trading", "台股": "Taiwan stock market",
        "美股": "US stock market Wall Street", "房地產": "real estate",
        "銀行": "banking finance", "保險": "insurance",
        "半導體": "semiconductor chip", "晶片": "semiconductor chip",
        "台積電": "TSMC semiconductor", "tsmc": "TSMC semiconductor",
        "nvidia": "NVIDIA GPU", "輝達": "NVIDIA GPU",
    }
    for kw, en in _TOPIC_MAP.items():
        if kw in text and en not in found:
            found.append(en)
    if found:
        return "featuring " + " and ".join(found[:2]) + " imagery"
    return ""


def _pick_cover_prompt(mood: str, hook: str = "", what: str = "",
                       style_modifier: bool = True) -> str:
    """從 _COVER_PROMPTS 隨機選取一個場景變體，並注入文章主題 + 隨機風格修飾。
    優先生成與文章主題直接相關的封面圖。"""
    topic_hint = _extract_topic_keywords(hook, what)

    # 若有明確主題，直接以主題為核心生成 prompt（不用預設場景）
    if topic_hint and hook:
        # 用文章標題的英文翻譯構建更貼合主題的 prompt
        hook_clean = hook.replace("\n", " ").strip()[:60]
        topic_prompt = (
            f"Cinematic editorial illustration about {topic_hint.replace('featuring ', '').replace(' imagery', '')}, "
            f"dramatic lighting, professional news media cover art, "
            f"dark moody background with accent lighting, "
            f"high-quality digital art, square format"
        )
        if style_modifier:
            style = random.choice(_STYLE_MODIFIERS)
            topic_prompt = topic_prompt.rstrip().rstrip(",") + f", {style}"
        return topic_prompt

    # 無明確主題時才 fallback 到預設場景
    variants = _COVER_PROMPTS.get(mood, _COVER_PROMPTS["default"])
    prompt = random.choice(variants)

    if topic_hint:
        prompt = prompt.replace("square format", f"{topic_hint}, square format")

    # 附加隨機風格修飾語
    if style_modifier:
        style = random.choice(_STYLE_MODIFIERS)
        prompt = prompt.rstrip().rstrip(",") + f", {style}"

    return prompt


_COVER_HISTORY_PATH = Path(__file__).parent / "cover_history.json"
_COVER_HISTORY_WINDOW = 10  # how many recent covers to compare against


def _load_cover_history() -> list[dict]:
    """Load recent cover history from JSON file."""
    try:
        if _COVER_HISTORY_PATH.exists():
            return json.loads(_COVER_HISTORY_PATH.read_text())
    except Exception:
        pass
    return []


def _save_cover_history(entry: dict) -> None:
    """Append a cover entry to history, keeping only the last _COVER_HISTORY_WINDOW entries."""
    history = _load_cover_history()
    history.append(entry)
    history = history[-_COVER_HISTORY_WINDOW:]
    try:
        _COVER_HISTORY_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"   ⚠️ 封面歷史寫入失敗：{e}")


def _pick_diverse_cover_prompts(mood: str, count: int = 3,
                                hook: str = "", what: str = "") -> list[str]:
    """從 _COVER_PROMPTS 選取 count 個不同場景變體（若不夠則允許重複但換風格）。
    同時對比最近 10 張封面歷史，避免相同 mood+style 組合重複出現。"""
    variants = list(_COVER_PROMPTS.get(mood, _COVER_PROMPTS["default"]))
    random.shuffle(variants)
    topic_hint = _extract_topic_keywords(hook, what)

    # Load recent history to avoid repeating mood+style+variant_index combos
    history = _load_cover_history()
    recently_used = set()
    for entry in history[-_COVER_HISTORY_WINDOW:]:
        recently_used.add((entry.get("mood", ""), entry.get("style", ""),
                           entry.get("variant_idx", -1)))

    prompts = []
    used_styles = []
    saved_entries = []

    for i in range(count):
        # Try to find a variant+style combo not seen in recent history
        best_variant_idx = None
        best_style = None

        for attempt_vi in range(len(variants)):
            vi = (i + attempt_vi) % len(variants)
            available_styles = [s for s in _STYLE_MODIFIERS
                                 if s not in used_styles
                                 and (mood, s, vi) not in recently_used]
            if available_styles:
                best_variant_idx = vi
                best_style = random.choice(available_styles)
                break

        # Fallback: pick any unused style regardless of history
        if best_variant_idx is None:
            best_variant_idx = i % len(variants)
            fallback_styles = [s for s in _STYLE_MODIFIERS if s not in used_styles]
            if not fallback_styles:
                fallback_styles = list(_STYLE_MODIFIERS)
            best_style = random.choice(fallback_styles)

        used_styles.append(best_style)
        base = variants[best_variant_idx]

        # 注入文章主題
        if topic_hint:
            base = base.replace("square format", f"{topic_hint}, square format")

        prompt = base.rstrip().rstrip(",") + f", {best_style}"
        prompts.append(prompt)
        saved_entries.append({
            "mood": mood,
            "style": best_style,
            "variant_idx": best_variant_idx,
            "ts": int(time.time()),
        })

    # Persist the first selected entry (the one that will actually be used as cover)
    if saved_entries:
        _save_cover_history(saved_entries[0])

    return prompts


def _build_person_prompt(person: str, mood: str) -> str:
    """為有人物的文章生成藝術風格 prompt（漫畫/普普/賽博龐克）"""
    # 情緒 → 藝術風格 + 場景（與 _COVER_PROMPTS 一致）
    mood_style = {
        "crash": (
            "Marvel comic book style dramatic illustration",
            "at a tense press conference with red financial charts crashing behind, "
            "stressed expression, bold ink outlines, action lines, halftone shading, "
            "intense red and orange colors"
        ),
        "bullish": (
            "Andy Warhol pop art style portrait, mature man with short gray silver hair, clean shaven face, wearing dark suit, Bitcoin gold coin halo above his head, Bitcoin symbols surrounding him, bold flat color blocks in gold yellow orange and white, halftone dots, pop art, square format",
            "confident smile, radiant divine golden light rays behind, epic cryptocurrency evangelist, vibrant comic book style colors, ultra detailed face"
        ),
        "regulation": (
            "Cyberpunk digital illustration",
            "at a futuristic government hearing with neon hologram screens, "
            "dramatic purple and cyan lighting, dark tech atmosphere, bold outlines"
        ),
        "etf": (
            "Andy Warhol pop art style vibrant illustration",
            "at a corporate announcement event with golden Bitcoin imagery, "
            "bold flat colors in gold navy and white, halftone dots, wealth theme"
        ),
        "hack": (
            "Cyberpunk digital illustration",
            "in a dark cybersecurity command center with multiple screens showing code, "
            "green matrix-like text, neon purple and cyan lighting, bold outlines"
        ),
        "default": (
            "Andy Warhol pop art style vibrant illustration",
            "at a cryptocurrency conference with colorful trading charts behind, "
            "bold flat color blocks, halftone dots, vibrant colors"
        ),
    }
    style, scene = mood_style.get(mood, mood_style["default"])
    return (
        f"{style} of {person}, {scene}, square format"
    )


def generate_ai_cover(hook: str, what: str = "",
                      person: str = "",
                      forced_mood: str = None) -> Optional[Image.Image]:
    """用 fal-ai FLUX schnell 根據文章情緒生成 AI 封面圖。
    如果有人物名稱，生成該人物的場景照片。
    forced_mood: 若有值，強制使用指定情緒（不自動偵測）。"""
    fal_key = os.environ.get("FAL_KEY", "").strip()
    if not fal_key:
        return None
    try:
        import subprocess as _sp
        mood = forced_mood or _detect_article_mood(hook, what)
        if person:
            prompt = _build_person_prompt(person, mood)
            print(f"   🎨 AI 封面生成中... (人物: {person}, 情緒: {mood})")
        else:
            prompt = _pick_cover_prompt(mood, hook, what)
            print(f"   🎨 AI 封面生成中... (情緒: {mood})")

        result = _sp.run(
            ["curl", "-s", "-X", "POST", "https://fal.run/fal-ai/flux-pro/v1.1",
             "-H", f"Authorization: Key {fal_key}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "prompt": prompt,
                 "image_size": "square_hd",
                 "num_images": 1,
                 "safety_tolerance": "5",
             })],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"   ⚠️ fal-ai 呼叫失敗：exit {result.returncode}")
            return None
        data = json.loads(result.stdout)
        img_url = data["images"][0]["url"]
        img = download_image(img_url)
        if img:
            print(f"   ✅ AI 封面下載完成 ({mood})")
        return img
    except Exception as e:
        print(f"   ⚠️ AI 封面生成失敗：{e}")
        return None


def generate_ai_cover_candidates(
    hook: str, what: str = "", person: str = "",
    count: int = 3, out_dir: str = ""
) -> list[str]:
    """生成多張 AI 封面候選圖，存到 out_dir，回傳檔案路徑列表。
    用於 draft 階段讓老闆從中挑選。每張用不同 seed 確保變化。"""
    fal_key = os.environ.get("FAL_KEY", "").strip()
    if not fal_key:
        print("   ⚠️ FAL_KEY 未設定，跳過封面候選生成")
        return []

    import subprocess as _sp
    mood = _detect_article_mood(hook, what)
    if person:
        # 人物模式：每張用相同 prompt 但不同 seed
        prompts = [_build_person_prompt(person, mood)] * count
        print(f"   🎨 生成 {count} 張封面候選 (人物: {person}, 情緒: {mood})")
    else:
        # 無人物模式：每張用不同場景變體 + 不同風格
        prompts = _pick_diverse_cover_prompts(mood, count, hook, what)
        print(f"   🎨 生成 {count} 張封面候選 (情緒: {mood}, 各用不同場景)")

    saved_paths: list[str] = []
    for idx in range(count):
        try:
            seed = int(time.time() * 1000) + idx * 137  # 不同 seed 確保變化
            current_prompt = prompts[idx] if idx < len(prompts) else prompts[-1]
            print(f"   📝 候選 {idx+1} prompt: {current_prompt[:80]}...")
            result = _sp.run(
                ["curl", "-s", "-X", "POST", "https://fal.run/fal-ai/flux-pro/v1.1",
                 "-H", f"Authorization: Key {fal_key}",
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps({
                     "prompt": current_prompt,
                     "image_size": "square_hd",
                     "num_images": 1,
                     "safety_tolerance": "5",
                     "seed": seed,
                 })],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                print(f"   ⚠️ 候選 {idx+1} 生成失敗：exit {result.returncode}")
                continue
            data = json.loads(result.stdout)
            img_url = data["images"][0]["url"]
            img = download_image(img_url)
            if img and out_dir:
                path = os.path.join(out_dir, f"cover_candidate_{idx+1}.jpg")
                img.save(path, "JPEG", quality=92)
                saved_paths.append(path)
                print(f"   ✅ 候選 {idx+1} 已存：{path}")
            elif img:
                # 沒指定目錄，存到暫存
                path = f"/tmp/cover_candidate_{idx+1}.jpg"
                img.save(path, "JPEG", quality=92)
                saved_paths.append(path)
                print(f"   ✅ 候選 {idx+1} 已存：{path}")
        except Exception as e:
            print(f"   ⚠️ 候選 {idx+1} 失敗：{e}")

    print(f"   📋 共生成 {len(saved_paths)}/{count} 張封面候選")
    return saved_paths


def get_pexels_photo(keywords: str, slide_idx: int = 0) -> Optional[Image.Image]:
    """Pexels API 抓高品質主題照片（用 curl 避免 Cloudflare 擋 urllib）"""
    api_key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        import subprocess as _sp
        from urllib.parse import quote
        query = keywords.replace(",", " ")
        # 用 slide_idx 決定 page，避免所有 slide 選同一批照片
        page = (slide_idx // 15) + 1
        url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=15&page={page}&orientation=square"
        result = _sp.run(
            ["curl", "-s", "-H", f"Authorization: {api_key}", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if not photos:
            return None
        photo = photos[slide_idx % len(photos)]
        print(f"   📸 Pexels [{keywords}] / {photo['photographer']}")
        return download_image(photo["src"]["large"])
    except Exception as e:
        print(f"   ⚠️ Pexels 失敗：{e}")
        return None


def get_og_photo(article_url: str) -> Optional[Image.Image]:
    """取得文章 OG 封面圖（Slide 1 專用）"""
    global _og_cache
    if not article_url:
        return None
    if article_url not in _og_cache:
        og_url = fetch_og_image(article_url)
        if og_url:
            print(f"   📷 文章原圖：{og_url[:70]}...")
            img = download_image(og_url)
            _og_cache[article_url] = img
        else:
            _og_cache[article_url] = None
    return _og_cache.get(article_url)


def get_keyword_photo(keywords: str, seed: str = "", slide_idx: int = 0) -> Optional[Image.Image]:
    """用關鍵字抓主題照片
    優先序：Pexels（精準）→ Unsplash（高品質）→ loremflickr（免費）→ picsum（fallback）
    """
    # 1. Pexels（有 API key 時，最精準）
    img = get_pexels_photo(keywords, slide_idx)
    if img:
        return img

    # 2. loremflickr：免費真實照片
    try:
        import time as _time
        kw = keywords.replace(" ", ",")
        seed_n = abs(hash(f"{seed}-{slide_idx}-{int(_time.time())}")) % 999999
        url = f"https://loremflickr.com/1080/1080/{kw}?random={seed_n}&lock={seed_n}"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=12) as r:
            data = r.read()
        img = Image.open(BytesIO(data)).convert("RGB")
        if img.size[0] >= 200:
            print(f"   🌄 loremflickr [{keywords}]")
            return img
    except Exception as e:
        print(f"   ⚠️ loremflickr 失敗：{e}")

    # 3. picsum 最終 fallback
    seed_hash = hashlib.md5(f"{seed}-{slide_idx}".encode()).hexdigest()[:10]
    print(f"   🎲 picsum fallback (seed={seed_hash})...")
    return download_image(f"https://picsum.photos/seed/{seed_hash}/1080/1080")


def get_photo(article_url: str, keyword: str, seed: str = "", slide_idx: int = 0) -> Optional[Image.Image]:
    """舊介面相容（CLI 單張用）"""
    if slide_idx == 0 and article_url:
        img = get_og_photo(article_url)
        if img:
            return img
    seed_hash = hashlib.md5(f"{seed}-{slide_idx}".encode()).hexdigest()[:10]
    print(f"   🎲 picsum (seed={seed_hash})...")
    return download_image(f"https://picsum.photos/seed/{seed_hash}/1080/1080")


# ── 背景製作（支援裁切偏移）──────────────────────────────────

def make_background(photo: Optional[Image.Image], theme: dict,
                    W=1080, H=1080, crop_x: int = 0, crop_y: int = 0,
                    cover: bool = False,
                    palette: dict = None, slide_idx: int = 0,
                    article_seed: str = "") -> Image.Image:
    """
    cover=True → Slide 1 封面模式：照片更亮、模糊更少、漸層只在下半部
    cover=False → 一般 Slide：照片暗化 + 全圖漸層（適合放大量文字）
    palette → 配色主題（用於程式化背景）
    """
    accent = theme["accent"]
    if photo is None:
        if palette:
            # 有配色主題：用程式化生成背景（algorithmic-art 風格）
            return generate_art_background(W, H, palette, slide_idx, article_seed)
        # 無配色主題時：簡單深色漸層 fallback
        bg = Image.new("RGB", (W, H), (12, 12, 18))
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for y in range(H):
            ratio = y / H
            a = int(40 * ratio * ratio)
            d.line([(0, y), (W, y)], fill=(*accent, a))
        for y in range(H // 3):
            a = int(8 * (1 - y / (H / 3)))
            d.line([(0, y), (W, y)], fill=(*accent, a))
        return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    pw, ph = photo.size
    if pw / ph > 1:
        new_h = H
        new_w = int(H * pw / ph)
    else:
        new_w = W
        new_h = int(W * ph / pw)

    # 確保縮放後夠大
    if new_w < W + abs(crop_x) * 2:
        new_w = W + abs(crop_x) * 2
        new_h = int(new_w * ph / pw)
    if new_h < H + abs(crop_y) * 2:
        new_h = H + abs(crop_y) * 2
        new_w = int(new_h * pw / ph)

    try:
        photo = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
    except AttributeError:
        photo = photo.resize((new_w, new_h), Image.LANCZOS)

    base_x = (new_w - W) // 2
    base_y = (new_h - H) // 2
    off_x = max(0, min(new_w - W, base_x + crop_x))
    off_y = max(0, min(new_h - H, base_y + crop_y))
    photo = photo.crop((off_x, off_y, off_x + W, off_y + H))

    if cover:
        # 封面模式：照片清晰亮眼，只在下半漸層（讓標題可讀）
        photo = photo.filter(ImageFilter.GaussianBlur(radius=0.3))
        photo = ImageEnhance.Brightness(photo).enhance(0.62)
        photo = ImageEnhance.Contrast(photo).enhance(1.15)
        r, g, b = theme["overlay"]
        gradient = Image.new("L", (1, H))
        for y in range(H):
            # 上面 40% 幾乎透明，下面 60% 快速加深
            if y < H * 0.35:
                a = 30
            else:
                ratio = (y - H * 0.35) / (H * 0.65)
                a = int(30 + 200 * ratio)
            gradient.putpixel((0, y), min(a, 240))
        gradient = gradient.resize((W, H))
        overlay = Image.new("RGBA", (W, H), (r, g, b, 0))
        overlay.putalpha(gradient)
    else:
        # 一般模式：暗化 + 全圖漸層
        photo = photo.filter(ImageFilter.GaussianBlur(radius=0.8))
        photo = ImageEnhance.Brightness(photo).enhance(0.42)
        r, g, b = theme["overlay"]
        min_a, max_a = theme["overlay_min_alpha"], theme["overlay_max_alpha"]
        gradient = Image.new("L", (1, H))
        for y in range(H):
            gradient.putpixel((0, y), int(min_a + (max_a - min_a) * (y / H)))
        gradient = gradient.resize((W, H))
        overlay = Image.new("RGBA", (W, H), (r, g, b, 0))
        overlay.putalpha(gradient)

    return Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB")


# ── 頂部裝飾（Editorial）──────────────────────────────────────

def draw_top_bar(draw, theme, slide_info: str, W: int):
    """頂部金色線 + 右上頁碼（簡潔版）"""
    accent = theme["accent"]
    draw.rectangle([0, 0, W, 6], fill=accent)
    # 右上頁碼
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))


def draw_bottom_bar(draw, theme, W: int, H: int):
    """Slide 1 & 5 的底部黑條（品牌標識）"""
    accent = theme["accent"]
    draw.rectangle([0, H - 80, W, H], fill=(0, 0, 0))
    draw.rectangle([0, H - 5, W, H], fill=accent)
    font_en = get_font(26)
    draw.text((150, H - 55), theme["name_en"], fill=(160, 160, 160), font=font_en)


def draw_minimal_top(draw, theme, slide_info: str, W: int, H: int):
    accent = theme["accent"]
    draw.rectangle([0, 0, W, 3], fill=accent)
    font = get_font(22)
    draw.text((50, 24), theme["name"], fill=(150, 150, 150), font=font)
    draw.text((W - 88, 24), slide_info, fill=(100, 100, 100), font=font)


def draw_minimal_bottom(draw, theme, W: int, H: int):
    draw.rectangle([0, H - 3, W, H], fill=theme["accent"])


# ── 半透明文字背景區塊 ────────────────────────────────────────

def text_bg(draw, x1, y1, x2, y2, alpha=160):
    """在文字後面畫半透明黑底，增加可讀性"""
    overlay = Image.new("RGBA", (x2 - x1, y2 - y1), (0, 0, 0, alpha))
    # 直接在 draw 的 image 上合成
    try:
        draw._image.paste(overlay, (x1, y1), overlay)
    except Exception:
        pass  # 如果失敗就跳過（純文字仍可讀）


# ── SLIDE 1：Hook 封面 ────────────────────────────────────────

def slide_hook(bg: Image.Image, theme: dict, title: str, what_preview: str,
               slide_info: str, out: str, person_mode: bool = False):
    W, H = 1080, 1080
    img = bg.copy()
    accent = theme["accent"]
    style = theme["style"]

    # 封面頂部光暈效果（canvas-design 風格）
    glow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_overlay)
    for y in range(H // 4):
        a = int(6 * (1 - y / (H / 4)))
        gd.line([(0, y), (W, y)], fill=(*accent, a))
    img = Image.alpha_composite(img.convert("RGBA"), glow_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    if style == "abmedia":
        # ── abmedia 風格：大照片 + 白色大標題 + 底部漸層 ──
        # 頂部主題色粗線 + 頁碼
        draw.rectangle([0, 0, W, 6], fill=accent)
        draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

        # 主標題（72-84pt 粗體，垂直居中偏下）
        font_title = get_font(78)
        # 限制每行最多 10 個中文字（不截斷帶 "..."）
        lines = smart_title_lines(title, max_per_line=10)
        line_h = 128  # 78pt 字體高約 94px，行距需 ≥128 才不重疊
        total_title_h = len(lines[:3]) * line_h

        if person_mode:
            title_y_start = max(650, H - total_title_h - 200)
        else:
            title_y_start = max(320, (H - total_title_h) // 2 + 60)

        # 下方漸層（底部 30% 淡出到黑）
        for gy in range(H // 3):
            alpha = int(200 * (gy / (H // 3)))
            text_bg(draw, 0, H - (H // 3) + gy, W, H - (H // 3) + gy + 1, alpha=alpha)

        # IG safe zone: 8%-92% X, 10%-90% Y
        _safe_x_min = int(W * 0.08)
        _safe_x_max = int(W * 0.92)
        _safe_y_max = int(H * 0.90)

        # Draw title lines, clamped to safe zone
        y = title_y_start
        for line in lines[:3]:
            # Max width within safe zone
            max_line_px = _safe_x_max - _safe_x_min - 40
            # Instead of truncating with "...", reduce font size
            if tw(draw, line, font_title) > max_line_px:
                # Try smaller font
                font_title_sm = get_font(64)
                if tw(draw, line, font_title_sm) > max_line_px:
                    font_title_sm = get_font(56)
                lx = cx(draw, line, font_title_sm, W)
                lx = max(_safe_x_min, lx)
                draw_shadow_text(draw, (lx, y), line, font_title_sm,
                               fill=(255, 255, 255), offset=4)
            else:
                lx = cx(draw, line, font_title, W)
                lx = max(_safe_x_min, lx)
                draw_shadow_text(draw, (lx, y), line, font_title,
                               fill=(255, 255, 255), offset=4)
            y += line_h
            if y > _safe_y_max:
                break

        # 滑動提示（底部條上方）
        hint = "← 滑動查看完整分析 →"
        draw.text((cx(draw, hint, get_font(26), W), H - 80),
                  hint, fill=(220, 220, 220), font=get_font(26))

    elif style == "editorial":
        # ── 鏈新聞風格：大張照片 + 聳動標題居中 ──
        # 頂部主題色粗線 + 頁碼
        draw.rectangle([0, 0, W, 6], fill=accent)
        draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

        # 主標題（超大字，垂直居中偏下）
        font_title = get_font(92)
        lines = smart_title_lines(title, max_per_line=10)
        line_h = 112
        total_title_h = len(lines[:3]) * line_h

        if person_mode:
            title_y_start = max(650, H - total_title_h - 200)
        else:
            title_y_start = max(320, (H - total_title_h) // 2 + 60)

        # 標題文字背景區（半透明黑底）
        pad_x, pad_y = 40, 24
        bg_y1 = title_y_start - pad_y
        bg_y2 = min(title_y_start + total_title_h + pad_y, H - 80)
        text_bg(draw, 0, bg_y1, W, bg_y2, alpha=140 if person_mode else 120)

        # 左側主題色粗線
        draw.rectangle([60, bg_y1 + 10, 70, bg_y2 - 10], fill=accent)

        # IG safe zone: 100px from each edge prevents thumbnail cropping
        _cover_safe_margin = 100
        _cover_max_px = W - _cover_safe_margin * 2  # 880px
        y = title_y_start
        for line in lines[:3]:
            line = clamp_line(draw, line, font_title, _cover_max_px)
            lx = cx(draw, line, font_title, W)
            lx = max(_cover_safe_margin, lx)  # enforce left safe margin
            draw_shadow_text(draw, (lx, y), line, font_title,
                             fill=(255, 255, 255), offset=4)
            y += line_h

        # 主題色分割線
        bar_y = y + 12
        draw.rectangle([W // 2 - 70, bar_y, W // 2 + 70, bar_y + 4], fill=accent)


        # 底部品牌條
        draw_bottom_bar(draw, theme, W, H)

        # 滑動提示（底部條上方）
        hint = "← 滑動查看完整分析 →"
        draw.text((cx(draw, hint, get_font(26), W), H - 112),
                  hint, fill=(220, 220, 220), font=get_font(26))

    else:  # minimal
        draw_minimal_top(draw, theme, slide_info, W, H)
        draw_minimal_bottom(draw, theme, W, H)
        draw.rectangle([50, 90, W - 50, 92], fill=(60, 60, 60))

        font_title = get_font(72)
        lines = smart_wrap(title, width=13)
        total_h = len(lines[:3]) * 90
        y = (H - total_h) // 2 - 60
        for line in lines[:3]:
            lx = cx(draw, line, font_title, W)
            draw_shadow_text(draw, (lx, y), line, font_title, fill=(255, 255, 255))
            y += 90

        draw.rectangle([W // 2 - 60, y + 20, W // 2 + 60, y + 22], fill=accent)
        if what_preview:
            font_p = get_font(28)
            preview_lines = smart_wrap(what_preview, width=22)[:2]
            yp = y + 40
            for pl in preview_lines:
                draw.text((cx(draw, pl, font_p, W), yp), pl,
                          fill=(160, 160, 160), font=font_p)
                yp += 40

        hint = "← 左滑查看詳情 →"
        draw.text((cx(draw, hint, get_font(24), W), H - 50),
                  hint, fill=(170, 170, 170), font=get_font(24))

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Slide 1 → {Path(out).name}")


# ── SLIDE 2：發生了什麼（全頁，無底條）──────────────────────── # DEPRECATED

def slide_what(bg: Image.Image, theme: dict, text: str, slide_info: str, out: str):
    W, H = 1080, 1080
    img = bg.copy()
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    style = theme["style"]

    if style == "editorial":
        M = 100
        draw_top_bar(draw, theme, slide_info, W)

        # 大標題（金色）+ 裝飾線
        draw_shadow_text(draw, (M, 70), "發生了什麼？",
                         get_font(52), fill=accent)
        draw.rectangle([M, 134, M + 120, 138], fill=accent)

        # 內文（自適應填滿全頁，垂直置中）
        header_bottom = 166
        available_h = H - header_bottom - 40
        # 安全限制：確保不超高
        max_allowed_lines = int(available_h / 36)
        font_size, line_h, wrap_w = fit_text_params(text, available_h,
                                                      max_width_px=860,
                                                      max_lines=max_allowed_lines)
        font_body = get_font(font_size)
        max_lines = int(available_h / line_h)
        wrapped = smart_wrap(text, width=wrap_w)[:max_lines]
        content_h = len(wrapped) * line_h
        y = header_bottom + max(0, (available_h - content_h) // 2)

        max_text_px = W - M - 80  # 右邊距留 80px
        for line in wrapped:
            line = clamp_line(draw, line, font_body, max_text_px)
            draw.text((M, y), line, fill=(235, 235, 235), font=font_body)
            y += line_h
            if y > H - 40:
                break

    else:  # minimal
        draw_minimal_top(draw, theme, slide_info, W, H)
        draw_minimal_bottom(draw, theme, W, H)
        draw.rectangle([50, 90, W - 50, 92], fill=(60, 60, 60))
        heading = "發生了什麼？"
        draw.text((cx(draw, heading, get_font(52), W), 130),
                  heading, fill=accent, font=get_font(52))
        draw.rectangle([W // 2 - 40, 196, W // 2 + 40, 199], fill=accent)
        header_bottom_m = 240
        available_h_m = H - header_bottom_m - 40
        max_allowed_m = int(available_h_m / 36)
        font_size, line_h, wrap_w = fit_text_params(text, available_h_m,
                                                      max_lines=max_allowed_m)
        wrapped = smart_wrap(text, width=wrap_w)[:20]
        content_h = len(wrapped) * line_h
        y = header_bottom_m + max(0, (available_h_m - content_h) // 2)
        max_text_px_m = W - 100  # 左右各留 50px
        for line in wrapped:
            line = clamp_line(draw, line, get_font(font_size), max_text_px_m)
            lx = cx(draw, line, get_font(font_size), W)
            draw.text((lx, y), line, fill=(215, 215, 215), font=get_font(font_size))
            y += line_h

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Slide 2 → {Path(out).name}")


# ── SLIDE 3：三大重點（標題 + 說明，全頁）────────────────────

# DEPRECATED
def slide_points(bg: Image.Image, theme: dict, points: list, slide_info: str, out: str):
    """
    points 格式：["標題|詳細說明", ...]
    如果沒有 | 分隔，整行當標題
    """
    W, H = 1080, 1080
    img = bg.copy()
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    style = theme["style"]

    if style == "editorial":
        M = 150
        draw_top_bar(draw, theme, slide_info, W)

        draw_shadow_text(draw, (M, 100), "三大重點",
                         get_font(58), fill=accent)
        draw.rectangle([M, 172, M + 120, 176], fill=accent)

        y = 215
        font_num  = get_font(30)
        font_head = get_font(44)  # 重點標題（大）
        font_desc = get_font(34)  # 說明（小）

        for i, point in enumerate(points[:3]):
            # 解析 "標題|說明" 格式
            if "|" in point:
                pt_title, pt_desc = point.split("|", 1)
            else:
                pt_title = point[:20]
                pt_desc  = point[20:] if len(point) > 20 else ""

            num = str(i + 1)
            # 金色數字方塊
            draw.rectangle([M, y, M + 50, y + 50], fill=accent)
            draw.text((M + (50 - tw(draw, num, font_num)) // 2, y + 9),
                      num, fill=(0, 0, 0), font=font_num)

            # 重點標題（金色）
            draw_shadow_text(draw, (M + 64, y + 4), pt_title.strip(),
                             font_head, fill=accent)

            # 說明文字（白色，最多3行）
            desc_y = y + 58
            for dline in smart_wrap(pt_desc.strip(), width=20)[:3]:
                draw.text((M + 64, desc_y), dline,
                          fill=(210, 210, 210), font=font_desc)
                desc_y += 42

            y = max(desc_y + 18, y + 150)
            if y > H - 80:
                break

    else:  # minimal
        draw_minimal_top(draw, theme, slide_info, W, H)
        draw_minimal_bottom(draw, theme, W, H)
        draw.rectangle([50, 90, W - 50, 92], fill=(60, 60, 60))
        heading = "三大重點"
        draw.text((cx(draw, heading, get_font(52), W), 130),
                  heading, fill=accent, font=get_font(52))
        draw.rectangle([W // 2 - 40, 196, W // 2 + 40, 199], fill=accent)
        y = 250
        for i, point in enumerate(points[:3]):
            if "|" in point:
                pt_title, pt_desc = point.split("|", 1)
            else:
                pt_title, pt_desc = point[:18], ""
            num_text = f"0{i + 1}"
            draw.text((50, y), num_text, fill=(80, 80, 80), font=get_font(26))
            draw.rectangle([50, y + 40, W - 50, y + 41], fill=(40, 40, 40))
            draw.text((cx(draw, pt_title.strip(), get_font(42), W), y + 5),
                      pt_title.strip(), fill=accent, font=get_font(42))
            if pt_desc.strip():
                for dl in smart_wrap(pt_desc.strip(), width=20)[:2]:
                    lx = cx(draw, dl, get_font(32), W)
                    draw.text((lx, y + 54), dl, fill=(190, 190, 190), font=get_font(32))
                    y += 36
            y = max(y + 130, y + 90)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Slide 3 → {Path(out).name}")


# ── 佐證照片頁：大圖 + 說明文字 ─────────────────────────────

# DEPRECATED
def slide_evidence(bg: Image.Image, theme: dict, evidence_text: str,
                   slide_info: str, out: str, channel: str = "crypto",
                   ai_data: Optional[dict] = None,
                   article_title: str = ""):
    """佐證頁：crypto/finance 用縮小走勢圖+註解，其他頻道用照片"""
    W, H = 1080, 1080
    accent = theme["accent"]
    ai_data = ai_data or {}

    # ── 嘗試取得走勢圖（只在明確提到特定幣種時才顯示）──
    chart_img = None
    chart_meta = {}
    chart_days = 7

    # 走勢圖偵測：優先用原始文章標題（最準），再用 AI 文字
    ai_text = (ai_data.get("hook", "") + ai_data.get("what", "") + evidence_text).lower()
    check_text = (article_title + " " + ai_text).lower()

    # 幣種辨識表：關鍵字 → CoinGecko ID
    _COIN_MAP = {
        "btc": "bitcoin", "比特幣": "bitcoin", "bitcoin": "bitcoin",
        "eth": "ethereum", "以太": "ethereum", "ethereum": "ethereum",
        "sol": "solana", "solana": "solana",
        "bnb": "binancecoin", "幣安幣": "binancecoin",
        "xrp": "ripple", "瑞波": "ripple",
        "ada": "cardano", "cardano": "cardano",
        "doge": "dogecoin", "狗狗幣": "dogecoin",
        "dot": "polkadot", "polkadot": "polkadot",
        "avax": "avalanche-2", "avalanche": "avalanche-2",
        "matic": "matic-network", "polygon": "matic-network",
        "link": "chainlink", "chainlink": "chainlink",
        "sui": "sui", "ton": "the-open-network",
    }

    # 商品辨識表：關鍵字 → (Yahoo Finance symbol, 中文標籤)
    _COMMODITY_MAP = {
        "黃金": ("GC=F", "黃金"), "gold": ("GC=F", "黃金"),
        "白銀": ("SI=F", "白銀"), "silver": ("SI=F", "白銀"),
        "原油": ("CL=F", "原油"), "oil": ("CL=F", "原油"),
        "wti": ("CL=F", "原油"), "布蘭特": ("BZ=F", "布蘭特原油"),
        "brent": ("BZ=F", "布蘭特原油"),
        "銅": ("HG=F", "銅"), "copper": ("HG=F", "銅"),
        "天然氣": ("NG=F", "天然氣"), "natural gas": ("NG=F", "天然氣"),
    }

    # 個股辨識表：關鍵字 → (Yahoo Finance symbol, 中文標籤)
    _STOCK_MAP = {
        "台積電": ("2330.TW", "台積電"), "tsmc": ("2330.TW", "台積電"),
        "2330": ("2330.TW", "台積電"),
        "鴻海": ("2317.TW", "鴻海"), "foxconn": ("2317.TW", "鴻海"),
        "聯發科": ("2454.TW", "聯發科"), "mediatek": ("2454.TW", "聯發科"),
        "nvidia": ("NVDA", "NVIDIA"), "輝達": ("NVDA", "NVIDIA"),
        "nvda": ("NVDA", "NVIDIA"),
        "tesla": ("TSLA", "Tesla"), "特斯拉": ("TSLA", "Tesla"),
        "apple": ("AAPL", "Apple"), "蘋果": ("AAPL", "Apple"),
        "microsoft": ("MSFT", "Microsoft"), "微軟": ("MSFT", "Microsoft"),
        "google": ("GOOGL", "Google"), "alphabet": ("GOOGL", "Google"),
        "meta": ("META", "Meta"),
        "amazon": ("AMZN", "Amazon"), "亞馬遜": ("AMZN", "Amazon"),
        "coinbase": ("COIN", "Coinbase"),
        "microstrategy": ("MSTR", "MicroStrategy"),
        "strategy": ("MSTR", "MicroStrategy"),
        "台股": ("^TWII", "台股加權"), "加權": ("^TWII", "台股加權"),
        "s&p": ("^GSPC", "S&P 500"), "標普": ("^GSPC", "S&P 500"),
        "nasdaq": ("^IXIC", "NASDAQ"), "那斯達克": ("^IXIC", "NASDAQ"),
        "道瓊": ("^DJI", "道瓊工業"), "dow jones": ("^DJI", "道瓊工業"),
    }

    _CRASH_KW = ["閃崩", "暴跌", "爆倉", "崩盤", "跳水", "插針", "清算",
                  "liquidat", "crash", "dump", "plunge", "flash"]
    is_crash = any(kw in check_text for kw in _CRASH_KW)

    # 從文章內容偵測幣種（優先匹配具體幣名，不要預設 BTC）
    detected_coin = None
    for kw, coin_id in _COIN_MAP.items():
        if kw in check_text:
            detected_coin = coin_id
            break

    # 偵測商品（黃金、白銀、原油等）
    detected_commodity = None
    for kw, (sym, lbl) in _COMMODITY_MAP.items():
        if kw in check_text:
            detected_commodity = (sym, lbl)
            break

    # 偵測個股/指數（TSMC、NVIDIA、台股等）
    detected_stock = None
    if not detected_coin and not detected_commodity:
        for kw, (sym, lbl) in _STOCK_MAP.items():
            if kw in check_text:
                detected_stock = (sym, lbl)
                break

    # 只在明確偵測到資產 + 是 crypto/finance 頻道時才放走勢圖
    if channel in ("crypto", "finance"):
        if detected_coin:
            chart_days = 1 if is_crash else 7
            chart_img, chart_meta = fetch_price_chart(
                detected_coin, days=chart_days, size=(960, 500)
            )
        elif detected_commodity:
            sym, lbl = detected_commodity
            chart_days = 1 if is_crash else 7
            chart_img, chart_meta = fetch_commodity_chart(
                symbol=sym, label=lbl, days=chart_days, size=(960, 500)
            )
        elif detected_stock:
            sym, lbl = detected_stock
            chart_days = 1 if is_crash else 7
            chart_img, chart_meta = fetch_commodity_chart(
                symbol=sym, label=lbl, days=chart_days, size=(960, 500)
            )

    # 基底：深色背景（不用照片，避免干擾走勢圖可讀性）
    if chart_img:
        img = Image.new("RGBA", (W, H), (18, 18, 22, 255))
    else:
        img = bg.copy().convert("RGBA")

    draw = ImageDraw.Draw(img)
    draw_top_bar(draw, theme, slide_info, W)

    # 標籤
    tag_font = get_font(24)
    tag_label = " 📈 即時走勢 " if chart_img else " 📷 新聞現場 "
    tag_w = tw(draw, tag_label, tag_font) + 20
    draw.rectangle([40, 50, 40 + tag_w, 88], fill=(*accent, 220))
    draw.text((50, 56), tag_label, fill=(0, 0, 0), font=tag_font)

    if chart_img:
        # ── 走勢圖模式：縮小圖表 + 上方標題 + 下方註解 ──
        # 標題區
        coin_label = chart_meta.get("coin", "BTC")
        title_font = get_font(42)
        time_label = "近 24 小時走勢" if chart_days == 1 else "近 7 日走勢"
        chart_title = f"{coin_label}/USD {time_label}"
        draw_shadow_text(draw, (60, 110), chart_title, title_font,
                         fill=(255, 255, 255), offset=3)
        draw.rectangle([60, 168, 180, 172], fill=accent)

        # 走勢圖：居中放置（960×500 → 貼在 y=200 ~ y=700）
        chart_x = (W - chart_img.width) // 2
        chart_y = 200
        img.paste(chart_img, (chart_x, chart_y), chart_img)
        draw = ImageDraw.Draw(img)  # 重新建立 draw

        # 金色分隔線
        sep_y = chart_y + chart_img.height + 20
        draw.rectangle([60, sep_y, W - 60, sep_y + 3], fill=accent)

        # 下方註解區：事件走勢註解 + evidence_text
        note_y = sep_y + 24
        note_font = get_font(30)
        draw.text((60, note_y), "📊 關鍵解讀", fill=accent, font=get_font(32))
        note_y += 48

        # 走勢圖事件註解（AI 生成或自動組合）
        chart_note = ai_data.get("chart_note", "")
        if not chart_note and chart_meta:
            coin_label = chart_meta.get("coin", "BTC")
            pct = chart_meta.get("pct", 0)
            arrow = chart_meta.get("arrow", "")
            hook = ai_data.get("hook", "")
            time_note = "24 小時" if chart_days == 1 else "近 7 日"
            chart_note = f"{hook}：{coin_label} {time_note} {arrow}{abs(pct):.1f}%"
        if chart_note:
            for line in smart_wrap(chart_note, width=28)[:2]:
                draw.text((60, note_y), line, fill=accent, font=note_font)
                note_y += 44
            note_y += 8  # 額外間距

        for line in smart_wrap(evidence_text, width=28)[:3]:
            draw.text((60, note_y), line, fill=(220, 220, 220), font=note_font)
            note_y += 44

        # 資料來源（根據資產類型顯示不同來源）
        src_font = get_font(22)
        src_label = "Yahoo Finance" if (detected_commodity or detected_stock) else "CoinGecko"
        draw.text((60, H - 50), f"資料來源：{src_label} | 即時數據",
                  fill=(120, 120, 120), font=src_font)
    else:
        # ── 照片模式 fallback ──
        char_count = len(evidence_text)
        bg_height = 320 if char_count > 80 else (260 if char_count > 40 else 220)
        text_bg(draw, 0, H - bg_height, W, H, alpha=180)
        draw.rectangle([50, H - bg_height + 20, 58, H - 50], fill=accent)

        f_size, lh, ww = (30, 44, 26) if char_count > 80 else (34, 50, 22)
        font_desc = get_font(f_size)
        y = H - bg_height + 30
        max_lines = int((bg_height - 60) / lh)
        for line in smart_wrap(evidence_text, width=ww)[:max_lines]:
            draw.text((75, y), line, fill=(240, 240, 240), font=font_desc)
            y += lh

    img.convert("RGB").save(out, "JPEG", quality=93)
    print(f"   ✅ {Path(out).name} ({'走勢圖' if chart_img else '佐證照片'})")


# ── 單點深度分析頁 ────────────────────────────────────────────

# DEPRECATED
def slide_single_point(bg: Image.Image, theme: dict, point_num: int,
                       point_text: str, slide_info: str, out: str):
    """單一重點：上半部深色文字區 + 下半部露出背景照片"""
    W, H = 1080, 1080
    img = bg.copy()
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    M = 90
    content_w = W - M * 2

    # ── 解析三段式 "標題|分析|📊數據" ──
    parts = point_text.split("|")
    pt_title = parts[0].strip() if len(parts) >= 1 else point_text[:20]
    pt_desc = parts[1].strip() if len(parts) >= 2 else ""
    pt_data = parts[2].strip() if len(parts) >= 3 else ""
    for pfx in ("📊 ", "📊"):
        if pt_data.startswith(pfx):
            pt_data = pt_data[len(pfx):].strip()

    # ── 先計算所有文字內容需要的高度 ──
    title_lines = smart_wrap(pt_title, width=16)[:2]
    title_block_h = 130 + len(title_lines) * 56 + 16  # 數字+標題+裝飾線

    # 說明文字：根據可用高度動態計算字體大小+行數限制
    # 每個 POINT 面板最大可用高度 = (H * 0.65)，留 35% 給背景照片
    max_panel_h = int(H * 0.68)
    # 先用最小字體估算行數，再往上試
    _desc_candidates = [(30, 44, 23), (28, 42, 21), (26, 40, 20), (24, 36, 19), (22, 34, 18)]
    fs, lh, ww = 26, 40, 20  # fallback
    # 可用給說明+數據的總高度（扣掉標題區塊+間距）
    desc_budget_h = max_panel_h - title_block_h - 100 - 50
    for _fs, _lh, _ww in _desc_candidates:
        est_lines = len(smart_wrap(pt_desc, width=_ww)) if pt_desc else 0
        est_h = est_lines * _lh
        if est_h <= desc_budget_h:
            fs, lh, ww = _fs, _lh, _ww
            break
    # 強制限制 max_desc_lines（確保不溢出）
    max_desc_lines = max(1, int(desc_budget_h / lh) - 1)
    desc_lines = smart_wrap(pt_desc, width=ww)[:max_desc_lines] if pt_desc else []
    desc_h = len(desc_lines) * lh

    # 數據卡片
    data_lh = 36
    data_lines = smart_wrap(pt_data, width=30)[:3] if pt_data else []
    data_box_h = (len(data_lines) * data_lh + 48) if data_lines else 0

    # ── 計算內容總高度 → 決定深色面板高度 ──
    padding = 50  # 各區塊間距固定
    content_total = title_block_h + padding + desc_h + padding + data_box_h + 30
    # 面板至少佔 55%，最多 68%（留 32% 給背景照片）
    panel_h = max(int(H * 0.55), min(content_total + 40, max_panel_h))

    # ── 繪製：上方深色面板 + 下方漸層過渡 ──
    text_bg(draw, 0, 0, W, panel_h, alpha=210)
    # 漸層過渡帶（panel_h → panel_h+80: alpha 從 180→0）
    for gy in range(80):
        alpha = int(180 * (1 - gy / 80))
        text_bg(draw, 0, panel_h + gy, W, panel_h + gy + 1, alpha=alpha)

    draw_top_bar(draw, theme, slide_info, W)

    # ═══ 垂直置中：計算內容總高度，居中在面板內 ═══
    # title_block: 130(數字) + title_lines*56 + 24(裝飾線間距)
    # desc_block: desc_h
    # gaps: padding between title/desc + padding between desc/data + bottom margin
    actual_content_h = title_block_h + padding + desc_h + 30
    if data_lines:
        actual_content_h += 24 + data_box_h  # gap + data box
    top_margin = 40  # minimum top margin for top bar
    y_start = max(top_margin, (panel_h - actual_content_h) // 2)

    # ═══ 繪製 A：大數字 + 標題 ═══
    y = y_start
    draw.text((M, y), f"0{point_num}", fill=(*accent, 70), font=get_font(110))
    y += 130

    font_title = get_font(46)
    for tl in title_lines:
        draw_shadow_text(draw, (M, y), tl, font_title, fill=accent)
        y += 56
    draw.rectangle([M, y + 2, M + 80, y + 6], fill=accent)
    y += 24

    # ═══ 繪製 B：說明文字（左側金色豎線）═══
    bar_start = y
    font_body = get_font(fs)
    max_text_w = content_w - 30  # 最大文字寬度（留右邊距）
    for line in desc_lines:
        if y + lh > panel_h - data_box_h - 30:
            break
        # 最終寬度檢查：如果超出右邊界就截斷加…
        line_w = tw(draw, line, font_body) if hasattr(draw, '_font') or True else 0
        if line_w > max_text_w:
            while len(line) > 1 and tw(draw, line + "…", font_body) > max_text_w:
                line = line[:-1]
            line = line + "…"
        draw.text((M + 18, y), line, fill=(230, 230, 230), font=font_body)
        y += lh
    bar_end = y
    if bar_end > bar_start:
        draw.rectangle([M, bar_start + 4, M + 5, bar_end - 4],
                       fill=(*accent, 100))

    # ═══ 繪製 C：數據引用卡片（緊接在說明之後）═══
    if data_lines:
        y += 24
        box_y = min(y, panel_h - data_box_h - 10)
        box_x = M - 10
        box_r = box_x + content_w + 20
        box_b = box_y + data_box_h
        text_bg(draw, box_x, box_y, box_r, box_b, alpha=140)
        draw.rectangle([box_x, box_y, box_x + 5, box_b], fill=accent)
        # 📊 + 數據文字
        draw.text((box_x + 18, box_y + 16), "📊",
                  fill=accent, font=get_font(30))
        d_font = get_font(27)
        dy = box_y + 20
        for dl in data_lines[:3]:
            draw.text((box_x + 56, dy), dl,
                      fill=(255, 220, 140), font=d_font)
            dy += data_lh

    # 面板底部金色分隔線
    draw.rectangle([0, panel_h - 2, W, panel_h], fill=(*accent, 90))

    # 底部小標籤（在照片區域上）
    tag_font = get_font(24)
    tag = f"▲ 重點 {point_num}"
    draw.text((W - M - tw(draw, tag, tag_font), H - 50),
              tag, fill=(*accent, 200), font=tag_font)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ {Path(out).name} (重點{point_num})")


# ── 歷史脈絡 / 未來展望頁 ────────────────────────────────────

# DEPRECATED
def slide_context(bg: Image.Image, theme: dict, text: str,
                  slide_info: str, out: str):
    """歷史背景或未來展望：時間軸風格，填滿整頁"""
    W, H = 1080, 1080
    img = bg.copy()
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    M = 100

    draw_top_bar(draw, theme, slide_info, W)

    # 標題
    draw_shadow_text(draw, (M, 70), "歷史脈絡",
                     get_font(52), fill=accent)
    draw.rectangle([M, 134, M + 120, 138], fill=accent)

    # 內容（自適應填滿全頁，垂直置中）
    header_bottom = 166
    available_h = H - header_bottom - 40
    max_allowed_lines = int(available_h / 36)
    font_size, line_h, wrap_w = fit_text_params(text, available_h,
                                                  max_width_px=860,
                                                  max_lines=max_allowed_lines)
    font_body = get_font(font_size)
    max_lines = int(available_h / line_h)
    wrapped = smart_wrap(text, width=wrap_w)[:max_lines]
    content_h = len(wrapped) * line_h
    y = header_bottom + max(0, (available_h - content_h) // 2)

    max_text_px = W - M - 80
    for line in wrapped:
        line = clamp_line(draw, line, font_body, max_text_px)
        draw.text((M, y), line, fill=(235, 235, 235), font=font_body)
        y += line_h
        if y > H - 40:
            break

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ {Path(out).name} (歷史脈絡)")


# ── SLIDE 4：為什麼重要（引言式，全頁）───────────────────────

# DEPRECATED
def slide_impact(bg: Image.Image, theme: dict, text: str, slide_info: str, out: str):
    W, H = 1080, 1080
    img = bg.copy()
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]
    style = theme["style"]

    if style == "editorial":
        M = 100
        draw_top_bar(draw, theme, slide_info, W)

        draw_shadow_text(draw, (M, 70), "為什麼重要？",
                         get_font(52), fill=accent)
        draw.rectangle([M, 134, M + 120, 138], fill=accent)

        # 內容（自適應填滿全頁，垂直置中）
        header_bottom = 166
        available_h = H - header_bottom - 40
        max_allowed_lines = int(available_h / 36)
        font_size, line_h, wrap_w = fit_text_params(text, available_h,
                                                      max_width_px=860,
                                                      max_lines=max_allowed_lines)
        font_body = get_font(font_size)
        max_lines = int(available_h / line_h)
        wrapped = smart_wrap(text, width=wrap_w)[:max_lines]
        content_h = len(wrapped) * line_h
        y = header_bottom + max(0, (available_h - content_h) // 2)

        max_text_px = W - M - 80
        for line in wrapped:
            line = clamp_line(draw, line, font_body, max_text_px)
            draw.text((M, y), line, fill=(235, 235, 235), font=font_body)
            y += line_h
            if y > H - 40:
                break

    else:  # minimal
        draw_minimal_top(draw, theme, slide_info, W, H)
        draw_minimal_bottom(draw, theme, W, H)
        draw.rectangle([50, 90, W - 50, 92], fill=(60, 60, 60))
        heading = "為什麼重要？"
        draw.text((cx(draw, heading, get_font(52), W), 130),
                  heading, fill=accent, font=get_font(52))
        draw.rectangle([W // 2 - 40, 196, W // 2 + 40, 199], fill=accent)
        header_bottom_m = 240
        available_h_m = H - header_bottom_m - 40
        max_allowed_m = int(available_h_m / 36)
        font_size, line_h, wrap_w = fit_text_params(text, available_h_m,
                                                      max_lines=max_allowed_m)
        wrapped = smart_wrap(text, width=wrap_w)[:20]
        content_h = len(wrapped) * line_h
        y = header_bottom_m + max(0, (available_h_m - content_h) // 2)
        max_text_px_m = W - 100
        for line in wrapped:
            line = clamp_line(draw, line, get_font(font_size), max_text_px_m)
            lx = cx(draw, line, get_font(font_size), W)
            draw.text((lx, y), line, fill=(215, 215, 215), font=get_font(font_size))
            y += line_h

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Slide 4 → {Path(out).name}")


# ── SLIDE 5：CTA（底條保留品牌感）───────────────────────────

# DEPRECATED
def slide_cta(bg: Image.Image, theme: dict, cta: str, account: str,
              slide_info: str, out: str, channel: str = "crypto"):
    W, H = 1080, 1080
    accent = theme["accent"]
    style = theme["style"]

    if style == "editorial":
        # 純深色漸層背景（不用 bg 照片，避免 Logo 重疊問題）
        img = Image.new("RGBA", (W, H), (12, 12, 16, 255))
        # 品牌色微光漸層（中間亮，上下暗）
        gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gradient)
        for y_pos in range(H):
            ratio = y_pos / H
            a = int(25 * (1 - abs(ratio - 0.5) * 2))
            gd.line([(0, y_pos), (W, y_pos)], fill=(*accent, a))
        img = Image.alpha_composite(img, gradient)
        draw = ImageDraw.Draw(img)

        draw_top_bar(draw, theme, slide_info, W)
        draw_bottom_bar(draw, theme, W, H)

        # Logo 圖片（取代 emoji）
        logo = load_logo(channel, target_w=380)
        if logo:
            lx = (W - logo.width) // 2
            ly = 150
            img.paste(logo, (lx, ly), logo)
            draw = ImageDraw.Draw(img)  # 重新建立 draw（paste 後需要）
            y = ly + logo.height + 30
        else:
            # fallback: 大 emoji
            font_big = get_font(120)
            emoji = theme["cta_emoji"]
            ex = cx(draw, emoji, font_big, W)
            draw.text((ex, 190), emoji, fill=(255, 255, 255), font=font_big)
            y = 380

        # CTA 主文
        font_cta = get_font(58)
        cta_lines = smart_wrap(cta, width=14)
        for line in cta_lines[:3]:
            lx = cx(draw, line, font_cta, W)
            draw_shadow_text(draw, (lx, y), line, font_cta, fill=(255, 255, 255))
            y += 74

        # 金色分割線
        y += 24
        draw.rectangle([W // 2 - 80, y, W // 2 + 80, y + 4], fill=accent)
        y += 30

        # Follow
        f1 = f"追蹤 @{account}"
        f1_font = get_font(38)
        draw.text((cx(draw, f1, f1_font, W), y), f1, fill=accent, font=f1_font)
        y += 56
        f2 = "留言告訴我你的看法！"
        f2_font = get_font(32)
        draw.text((cx(draw, f2, f2_font, W), y), f2,
                  fill=(180, 180, 180), font=f2_font)

    else:  # minimal
        img = bg.copy().convert("RGBA")
        draw = ImageDraw.Draw(img)
        draw_minimal_top(draw, theme, slide_info, W, H)
        draw_minimal_bottom(draw, theme, W, H)
        draw.rectangle([50, 90, W - 50, 92], fill=(60, 60, 60))

        font_big = get_font(110)
        emoji = theme["cta_emoji"]
        draw.text((cx(draw, emoji, font_big, W), 190), emoji,
                  fill=(200, 200, 200), font=font_big)

        font_cta = get_font(52)
        cta_lines = smart_wrap(cta, width=14)
        y = 370
        for line in cta_lines[:3]:
            draw.text((cx(draw, line, font_cta, W), y), line,
                      fill=(240, 240, 240), font=font_cta)
            y += 68

        y += 24
        draw.rectangle([W // 2 - 30, y, W // 2 + 30, y + 2], fill=accent)
        y += 24
        f1 = f"Follow @{account}"
        f1_font = get_font(32)
        draw.text((cx(draw, f1, f1_font, W), y), f1, fill=accent, font=f1_font)

    img.convert("RGB").save(out, "JPEG", quality=93)
    print(f"   ✅ Slide 5 → {Path(out).name}")


# ── abmedia 新式 Slide 函式 ────────────────────────────────────

def slide_keypoints_abmedia(bg: Image.Image, theme: dict, points: list,
                            slide_info: str, out: str):
    """新 abmedia 風格：Key Points 頁（3-4 個重點卡片）
    Dark background #0D0D0D with semi-transparent cards
    Improved styling: better padding, gradient accents, more prominent titles
    """
    W, H = 1080, 1080
    # 使用傳入的背景圖（algorithmic art），加上深色半透明遮罩
    if bg and isinstance(bg, Image.Image) and bg.size == (W, H):
        img = bg.copy().convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (13, 13, 13, 200))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (W, H), theme.get("bg_color", (13, 13, 13)))
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]

    # Top bar with page number
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

    # Section title — editorial left-aligned style (no ▶ symbol: renders as □ on STHeiti)
    title_font = get_font(52)
    section_title = "重點整理"
    lm = 90  # left margin
    # Accent vertical bar as editorial marker
    draw.rectangle([lm, 58, lm + 7, 128], fill=accent)
    draw.text((lm + 22, 60), section_title, fill=(255, 255, 255), font=title_font)
    # Full-width thin separator line
    draw.rectangle([lm, 144, W - lm, 148], fill=accent)

    # Card layout: single-column full-width cards (abmedia style)
    num_points = min(len(points), 4)
    card_w = int(W * 0.84)  # 84% width (8% margin each side)
    card_x = int(W * 0.08)  # left margin 8%
    start_y = 175
    # Calculate card height and spacing to fill available area evenly
    available_h = H - start_y - 120  # leave room for watermark
    card_gap = 16
    card_h = min(200, (available_h - card_gap * (num_points - 1)) // max(num_points, 1))

    for i, point in enumerate(points[:4]):
        y = start_y + i * (card_h + card_gap)
        _draw_abmedia_card_improved(draw, card_x, y, card_w, card_h,
                          f"{i+1:02d}", point[:80], accent)

    # Bottom watermark
    _draw_watermark_abmedia(draw, theme, W, H)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Key Points → {Path(out).name}")


def slide_faq_abmedia(bg: Image.Image, theme: dict, faqs: list,
                     slide_info: str, out: str):
    """新 abmedia 風格：FAQ/Analysis 頁（2-3 Q&A pairs）
    Dark background with semi-transparent answer cards
    Improved: 💬 emoji, better visual hierarchy, divider lines
    """
    W, H = 1080, 1080
    # 使用傳入的背景圖，加上深色半透明遮罩
    if bg and isinstance(bg, Image.Image) and bg.size == (W, H):
        img = bg.copy().convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (13, 13, 13, 200))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (W, H), theme.get("bg_color", (13, 13, 13)))
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]

    # Top bar
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

    # Section title — editorial left-aligned style (no ▶ symbol: renders as □ on STHeiti)
    title_font = get_font(52)
    section_title = "常見問題"
    lm = 90  # left margin
    # Accent vertical bar as editorial marker
    draw.rectangle([lm, 58, lm + 7, 128], fill=accent)
    draw.text((lm + 22, 60), section_title, fill=(255, 255, 255), font=title_font)
    # Full-width thin separator line
    draw.rectangle([lm, 144, W - lm, 148], fill=accent)

    # Draw Q&A pairs with improved layout
    y = 220
    num_faqs = min(len(faqs), 3)
    for i, faq_item in enumerate(faqs[:num_faqs]):
        # Parse faq_item — supports dict {"q":..,"a":..}, (q, a) tuple/list, or "Q|A" string
        if isinstance(faq_item, dict):
            q = str(faq_item.get("q", ""))[:100]
            a = str(faq_item.get("a", "詳見相關報導"))[:250]
        elif isinstance(faq_item, (tuple, list)) and len(faq_item) >= 2:
            q = str(faq_item[0]).strip()[:100]
            a = str(faq_item[1]).strip()[:250]
        elif isinstance(faq_item, str) and "|" in faq_item:
            q, a = faq_item.split("|", 1)
            q = q.strip()[:100]
            a = a.strip()[:250]
        else:
            q = str(faq_item)[:100]
            a = "詳見相關報導"

        # Draw Q in accent color + question in white (editorial distinction)
        q_font = get_font(34)
        q_prefix = "Q"
        q_prefix_w = tw(draw, q_prefix, q_font)
        draw.text((90, y), q_prefix, fill=accent, font=q_font)
        draw.text((90 + q_prefix_w, y), f"：{q}", fill=(255, 255, 255), font=q_font)
        y += 55

        # Draw A in semi-transparent card
        a_font = get_font(26)
        a_text = f"A. {a}"
        # Semi-transparent card background
        card_y = y
        # Pixel-based wrap: answer block inner width = (W - 85*2) - 2*25 padding ≈ 860
        card_lines = _wrap_to_pixels(draw, a_text, a_font, (W - 85 * 2) - 50)[:4]
        card_h = len(card_lines) * 40 + 32
        _draw_card_bg(draw, 85, card_y, W - 85, card_y + card_h, accent)

        # Draw answer text
        ay = card_y + 16
        for line in card_lines:
            draw.text((110, ay), line, fill=(224, 224, 224), font=a_font)
            ay += 42
        y = card_y + card_h + 40

        # Subtle divider line between Q&A groups (except last)
        if i < num_faqs - 1:
            draw.rectangle([100, y - 20, W - 100, y - 18], fill=(80, 80, 80))

    # Bottom watermark
    _draw_watermark_abmedia(draw, theme, W, H)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ FAQ → {Path(out).name}")


def slide_ending(bg: Image.Image, theme: dict, question: str,
                brand_name: str, slide_info: str, out: str):
    """新 abmedia 風格：Ending 頁（LOGO + Question）
    Solid dark background #0D0D0D with accent decorations
    Improved: better logo sizing, bolder question text, accent line decoration
    """
    W, H = 1080, 1080
    # 使用傳入的背景圖，加上深色半透明遮罩
    if bg and isinstance(bg, Image.Image) and bg.size == (W, H):
        img = bg.copy().convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (13, 13, 13, 180))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (W, H), theme.get("bg_color", (13, 13, 13)))
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]

    # Top bar
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

    # Brand name/logo — centered, prominent (editorial masthead style)
    brand_font = get_font(68)
    brand_y = int(H * 0.30)
    brand_w = tw(draw, brand_name, brand_font)
    bx = (W - brand_w) // 2
    # Thin accent rule ABOVE the brand (spans just over the brand width)
    rule_len = brand_w + 80
    rule_x0 = (W - rule_len) // 2
    draw.rectangle([rule_x0, brand_y - 18, rule_x0 + rule_len, brand_y - 14], fill=accent)
    draw.text((bx, brand_y), brand_name, fill=(255, 255, 255), font=brand_font)
    # Thin accent rule BELOW the brand (same length, mirrored)
    draw.rectangle([rule_x0, brand_y + 84, rule_x0 + rule_len, brand_y + 88], fill=accent)

    # "留言分享你的看法" prompt above the question
    prompt_font = get_font(26)
    prompt = "留言分享你的看法"
    px = (W - tw(draw, prompt, prompt_font)) // 2
    draw.text((px, brand_y + 110), prompt, fill=(140, 140, 140), font=prompt_font)

    # Question — centered, bold white, large
    question_font = get_font(44)
    question_y = int(H * 0.58)
    q_lines = smart_wrap(question, width=18)[:2]
    qy = question_y
    for line in q_lines:
        qx = (W - tw(draw, line, question_font)) // 2
        draw.text((qx, qy), line, fill=(255, 255, 255), font=question_font)
        qy += 58

    # Engagement hint below question
    hint_font = get_font(24)
    hint = "追蹤帳號 · 開啟通知 · 不錯過財經大事"
    hx = (W - tw(draw, hint, hint_font)) // 2
    draw.text((hx, qy + 16), hint, fill=(110, 110, 110), font=hint_font)

    # Bottom watermark
    _draw_watermark_abmedia(draw, theme, W, H)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Ending → {Path(out).name}")


def _draw_abmedia_card_improved(draw, x, y, w, h, number, text, accent):
    """Editorial journalism card: number badge on left, text block on right.
    Matches abmedia style — clean, professional, news-magazine feel.
    """
    # Card background — dark charcoal with slight opacity
    card_bg = Image.new("RGBA", (int(w), int(h)), (28, 28, 28, 200))
    draw._image.paste(card_bg, (int(x), int(y)), card_bg)

    # Left accent bar (5px, full card height)
    draw.rectangle([int(x), int(y), int(x) + 5, int(y) + int(h)], fill=accent)

    # Number badge — accent color, vertically centered in left column
    num_font = get_font(44)
    num_x = int(x) + 22
    num_y = int(y) + int(h) // 2 - 28  # vertically centered
    draw.text((num_x, num_y), number, fill=accent, font=num_font)

    # Text block — to the right of the number column
    text_x = int(x) + 108
    text_w_px = int(w) - 128  # available width after number column + right padding
    text_font = get_font(30)
    # Pixel-based wrap: measure actual rendered width so text never overflows the card
    text_lines = _wrap_to_pixels(draw, text, text_font, text_w_px)[:3]

    # Vertically center the text block within the card
    line_h = 44
    total_text_h = len(text_lines) * line_h
    ty = int(y) + (int(h) - total_text_h) // 2
    ty = max(int(y) + 10, ty)

    for i, line in enumerate(text_lines):
        # First line: bold white (title); subsequent lines: lighter gray (description)
        color = (255, 255, 255) if i == 0 else (185, 185, 185)
        draw.text((text_x, ty), line, fill=color, font=text_font)
        ty += line_h


def _draw_abmedia_card(draw, x, y, w, h, number, text, accent):
    """Draw a single abmedia-style card with number and text (legacy version)"""
    # Semi-transparent card background
    card_bg = Image.new("RGBA", (w, h), (255, 255, 255, 15))
    # Round corners effect (simple version)
    draw._image.paste(card_bg, (int(x), int(y)), card_bg)

    # Number (bold, large)
    num_font = get_font(52)
    draw.text((int(x) + 20, int(y) + 15), number, fill=accent, font=num_font)

    # Text (smaller, wrapped)
    text_font = get_font(24)
    text_lines = smart_wrap(text, width=14)[:2]
    ty = int(y) + 80
    for line in text_lines:
        draw.text((int(x) + 20, ty), line, fill=(224, 224, 224), font=text_font)
        ty += 35


def _draw_card_bg(draw, x1, y1, x2, y2, accent):
    """Draw a semi-transparent card background"""
    overlay = Image.new("RGBA", (int(x2 - x1), int(y2 - y1)), (255, 255, 255, 15))
    try:
        draw._image.paste(overlay, (int(x1), int(y1)), overlay)
    except Exception:
        pass


def _draw_watermark_abmedia(draw, theme, W, H):
    """Draw bottom watermark: brand name on left, IG handle on right"""
    watermark_font = get_font(20)
    name_en = theme.get("name_en", "CRYPTO NEWS")
    name_zh = theme.get("name", "幣圈大小事")
    watermark_left = name_en
    watermark_right = f"@{theme.get('ig', 'money.showtime')}"
    draw.text((90, H - 50), watermark_left, fill=(90, 90, 90), font=watermark_font)
    rw = tw(draw, watermark_right, watermark_font)
    draw.text((W - 90 - rw, H - 50), watermark_right, fill=(90, 90, 90), font=watermark_font)


def slide_analysis_abmedia(bg: Image.Image, theme: dict, title: str, text: str,
                           image: Optional[Image.Image] = None,
                           slide_info: str = "", out: str = ""):
    """新增 abmedia 風格：長文分析頁（段落標題 + 配圖 + 正文）

    用於深度分析内容：
    - 段落標題有彩色色塊背景
    - 可選配圖（方形）
    - 正文最多 250 字，完整段落，不跨頁斷裂
    - 底部品牌名
    """
    W, H = 1080, 1080
    # 使用傳入的背景圖，加上深色半透明遮罩
    if bg and isinstance(bg, Image.Image) and bg.size == (W, H):
        img = bg.copy().convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (13, 13, 13, 200))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (W, H), theme.get("bg_color", (13, 13, 13)))
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]

    # Top bar
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

    # Section title with accent background color block (no ▶: renders as □ on STHeiti)
    title_font = get_font(44)
    title_text = title  # e.g. "深度分析"
    title_y = 70

    # Measure title width for background block
    title_w = tw(draw, title_text, title_font)
    title_x = 80

    # Draw accent color block behind title
    draw.rectangle([title_x - 10, title_y - 8, title_x + title_w + 10, title_y + 50],
                   fill=accent)

    # Draw title in dark color on top of accent block
    draw.text((title_x, title_y), title_text, fill=(13, 13, 13), font=title_font)

    current_y = 145

    # Optional image (square format, centered)
    if image:
        img_size = 320
        img_x = (W - img_size) // 2
        img_y = current_y

        # Resize image to square
        img_resized = image.resize((img_size, img_size), Image.Resampling.LANCZOS)
        img.paste(img_resized, (img_x, img_y))

        current_y = img_y + img_size + 40

    # Text content (≤ 250 words, complete paragraph)
    text_font = get_font(28)
    text_lines = smart_wrap(text, width=26)

    # 動態計算可用行數（留 100px watermark 空間）
    line_h = 38
    max_lines = max(8, int((H - current_y - 100) / line_h))
    max_lines = min(len(text_lines), max_lines)
    text_y = current_y

    for i, line in enumerate(text_lines[:max_lines]):
        if text_y + 38 > H - 100:  # Leave space for watermark
            break
        draw.text((85, text_y), line, fill=(224, 224, 224), font=text_font)
        text_y += 38

    # Bottom watermark
    _draw_watermark_abmedia(draw, theme, W, H)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Analysis → {Path(out).name}")


def slide_bignumber_abmedia(bg: Image.Image, theme: dict, number: str, label: str,
                            description: str = "", slide_info: str = "", out: str = ""):
    """新增 abmedia 風格：大數字卡片（趨勢圖替代方案）

    用於展示關鍵數據：
    - 巨大數字居中（120pt equivalent，accent color）
    - 標籤（32pt）
    - 可選說明文字（28pt，灰色）
    """
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), theme.get("bg_color", (13, 13, 13)))
    draw = ImageDraw.Draw(img)
    accent = theme["accent"]

    # Top bar
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.text((W - 95, 18), slide_info, fill=(130, 130, 130), font=get_font(22))

    # Section title — editorial left-aligned style (no ▶: renders as □ on STHeiti)
    title_font = get_font(48)
    lm = 90
    draw.rectangle([lm, 58, lm + 7, 124], fill=accent)
    draw.text((lm + 22, 60), "關鍵數據", fill=(255, 255, 255), font=title_font)
    draw.rectangle([lm, 140, W - lm, 144], fill=accent)

    # Big number centered (120pt equivalent)
    number_font = get_font(120)
    number_y = int(H * 0.35)
    nx = (W - tw(draw, number, number_font)) // 2
    draw.text((nx, number_y), number, fill=accent, font=number_font)

    # Label below number (32pt)
    label_font = get_font(40)
    label_y = number_y + 140
    lx = (W - tw(draw, label, label_font)) // 2
    draw.text((lx, label_y), label, fill=(255, 255, 255), font=label_font)

    # Optional description (28pt, gray)
    if description:
        desc_font = get_font(28)
        desc_lines = smart_wrap(description, width=32)[:3]
        desc_y = label_y + 60
        for line in desc_lines:
            dx = (W - tw(draw, line, desc_font)) // 2
            draw.text((dx, desc_y), line, fill=(180, 180, 180), font=desc_font)
            desc_y += 42

    # Decorative lines
    draw.rectangle([W // 2 - 100, number_y - 50, W // 2 + 100, number_y - 46], fill=accent)
    draw.rectangle([W // 2 - 120, label_y + 50, W // 2 + 120, label_y + 54], fill=accent)

    # Bottom watermark
    _draw_watermark_abmedia(draw, theme, W, H)

    img.save(out, "JPEG", quality=93)
    print(f"   ✅ Big Number → {Path(out).name}")


# ── Claude 動態生成 Slide 圖片關鍵字 ─────────────────────────

def _claude_slide_keywords(ai_data: dict, channel: str) -> list:
    """讓 Claude 根據文案內容為每張 Slide 生成精準英文 Pexels 搜尋詞（10 張）"""
    try:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return [None] * SLIDE_COUNT
        client = anthropic.Anthropic(api_key=api_key)
        hook   = ai_data.get("hook", "")
        what   = ai_data.get("what", "")[:120]
        points = " | ".join(ai_data.get("points", []))[:150]
        impact = ai_data.get("impact", "")[:100]
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": f"""為 IG Carousel {SLIDE_COUNT} 張投影片各生成最適合的英文 Pexels 圖片搜尋詞（2-3 個詞，逗號分隔）。
只輸出 {SLIDE_COUNT} 行，Slide 1 和 Slide 3 輸出 null（用文章原圖），其他輸出英文搜尋詞。

文案：
HOOK: {hook}
WHAT: {what}
POINTS: {points}
IMPACT: {impact}
頻道: {channel}"""}]
        )
        lines = [l.strip() for l in msg.content[0].text.strip().splitlines() if l.strip()]
        result = [None if l.lower() in ("null", "none", "-") else l for l in lines[:SLIDE_COUNT]]
        while len(result) < SLIDE_COUNT:
            result.append(None)
        print(f"   🎯 Claude 關鍵字：{[r for r in result if r][:5]}...")
        return result
    except Exception as e:
        print(f"   ⚠️ Claude 關鍵字生成失敗：{e}")
        return [None] * SLIDE_COUNT


# ── Carousel 主函式（4-6 頁版，新 abmedia 風格）────────────────────────────────

def generate_carousel(channel: str, ai_data: dict, article_url: str,
                      source: str, out_dir: str,
                      article_title: str = "",
                      cover_photo_path: str = None) -> list[str]:
    """cover_photo_path: 若有值，強制使用指定本地圖片做封面（跳過 AI 生成）。"""
    """
    4-6 頁 Carousel (abmedia 風格)，動態調整頁數：
      1. 封面 (slide_hook - 大照片 + 標題)
      2. 核心要點 (slide_keypoints_abmedia - 3-4 卡片)
      3-4. 分析/FAQ 頁 (slide_faq_abmedia 或 slide_analysis_abmedia - 可選，當內容豐富時)
      末頁. 結尾頁 (slide_ending - LOGO + 問題)

    Dynamic slide count:
      - Base: 4 (Cover + KeyPoints + FAQ + Ending)
      - 若有 5+ 重點 或 豐富 FAQ → 5-6 頁（加入長文分析或大數字卡片）

    article_title: 原始文章標題（用於走勢圖偵測幣種，最準確）
    """
    theme = THEMES.get(channel, THEMES["crypto"])
    account = IG_ACCOUNTS.get(channel, "money.showtime")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    seed = ai_data.get("hook", channel)[:30]

    # 動態決定頁數：根據內容豐富度
    raw_points = ai_data.get("points", [])
    faq_items = ai_data.get("faqs", ai_data.get("points", []))[:3]
    impact_text = ai_data.get("impact", "")

    # 判斷內容豐富度
    has_rich_points = len(raw_points) >= 5
    has_rich_faq = len(faq_items) >= 3 and any("|" in item for item in faq_items)
    has_rich_impact = len(impact_text) > 200

    # 決定最終頁數：4 基礎 + 1 如有豐富內容
    if has_rich_impact or (has_rich_points and has_rich_faq):
        N = 5  # Cover + KeyPoints + Analysis/FAQ + Extra + Ending
    else:
        N = SLIDE_COUNT  # 4: Cover + KeyPoints + FAQ + Ending

    print(f"   📊 動態頁數：{N} 頁（豐富度：點數={len(raw_points)}, FAQ={len(faq_items)}, 分析={len(impact_text)} 字）")

    # 配色：使用頻道固定 accent，背景圖案用輪替 palette（不覆蓋 accent）
    palette = _pick_palette(seed)
    print(f"   🎨 頻道色：{theme['accent']} | 風格：abmedia")
    print(f"   📸 下載背景照片（{N} 張）...")

    # 優先用 Claude 動態生成關鍵字，失敗則用預設
    _claude_kws = _claude_slide_keywords(ai_data, channel)
    kw_default = SLIDE_PHOTO_KEYWORDS.get(channel, SLIDE_PHOTO_KEYWORDS["crypto"])

    # 擴展預設關鍵字以支持 5-6 頁
    while len(kw_default) < N:
        kw_default.append(theme["keyword"])

    slide_keywords = []
    for i in range(N):
        ck = _claude_kws[i] if i < len(_claude_kws) else None
        dk = kw_default[i] if i < len(kw_default) else None
        # Slide 1 和最後一頁用純 bg，不需要關鍵字
        if i in (0, N - 1):
            slide_keywords.append(None)
        elif ck:
            slide_keywords.append(ck)
        elif dk:
            slide_keywords.append(dk)
        else:
            slide_keywords.append(theme["keyword"])

    # 取得 OG 圖（Slide 1 封面用）
    og_photo = get_og_photo(article_url)

    # 人物照片（封面用）
    person = ai_data.get("person", "")
    person = person.strip() if person else ""
    has_person = person and person.lower() not in ("null", "none", "")

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _fetch_one_bg(i):
        """並行：取得第 i 張 slide 的背景圖片"""
        if i == 0:
            # Slide 1：封面（cover_photo_path 優先 → AI 生成 → OG 圖 → Pexels → 程式化背景）
            photo = None
            if cover_photo_path:
                try:
                    photo = Image.open(cover_photo_path).convert("RGB")
                    photo = photo.resize((1080, 1080), Image.LANCZOS)
                    src = f"指定照片 ({Path(cover_photo_path).name})"
                    print(f"   📸 使用指定封面照片：{cover_photo_path}")
                except Exception as e:
                    print(f"   ⚠️ 指定封面照片讀取失敗：{e}，改用 AI 生成")
                    photo = None

            if not photo:
                hook_text = ai_data.get("hook", "")
                what_text = ai_data.get("what", "")
                person_for_ai = person if has_person else ""
                photo = generate_ai_cover(hook_text, what_text, person=person_for_ai, forced_mood=ai_data.get("mood"))
                if photo:
                    src = "AI 封面"
            if not photo and og_photo:
                photo = og_photo
                src = "OG 圖"
            if not photo:
                for cover_kw in theme["keyword"].split():
                    photo = get_pexels_photo(cover_kw, i)
                    if photo:
                        src = f"Pexels ({cover_kw})"
                        break
            if not photo:
                src = "程式化生成"
            bg = make_background(photo, theme, cover=True,
                                 palette=palette, slide_idx=i, article_seed=seed)
            return (i, bg, src)
        else:
            # 其餘頁面：優先 Pexels 照片，失敗則用程式化背景
            kw = slide_keywords[i] if i < len(slide_keywords) else None
            photo = None
            src = "algorithmic-art"
            if kw:
                photo = get_pexels_photo(kw, i)
                if photo:
                    src = f"Pexels ({kw})"
            if photo:
                bg = make_background(photo, theme, cover=False,
                                     palette=palette, slide_idx=i, article_seed=seed)
            else:
                bg = generate_art_background(1080, 1080, palette, i, seed)
            return (i, bg, src)

    # ── 並行背景生成 ──────────────────────────────────────────────
    print(f"   🚀 並行生成 {N} 張背景...")
    bgs = [None] * N
    label_map = {}

    with ThreadPoolExecutor(max_workers=min(N, 6)) as executor:
        futures = {executor.submit(_fetch_one_bg, i): i for i in range(N)}
        for future in as_completed(futures):
            idx, bg, src = future.result()
            bgs[idx] = bg
            if src:
                label_map[idx] = src

    for i in range(N):
        if i in label_map:
            print(f"   ✅ Slide {i+1} 背景：{label_map[i]}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = []

    def p(n):
        path = str(Path(out_dir) / f"{channel}_{ts}_s{n:02d}.jpg")
        paths.append(path)
        return path

    # 準備內容
    what_preview = clean_preview(ai_data.get("what", ""), max_chars=200)

    # 提取重點（用於 keypoints 卡片）：title + description 都顯示
    keypoint_texts = []
    for pt in raw_points[:4]:
        if pt and "|" in pt:
            parts = pt.split("|", 1)
            title_part = parts[0].strip()
            desc_part = parts[1].strip() if len(parts) > 1 else ""
            # 合併：標題 + 換行 + 說明（最多 60 字）
            if desc_part:
                combined = f"{title_part}  {desc_part[:50]}"
            else:
                combined = title_part
            keypoint_texts.append(combined[:100])
        elif pt:
            keypoint_texts.append(pt[:100])
    # 不使用空洞佔位符 — 若要點不足就用較少卡片
    if not keypoint_texts:
        keypoint_texts = ["詳見內文完整分析"]

    brand_name = theme.get("name", "金融大小事")
    # CTA 淨化：只取第一行，濾掉 AI 亂填的檔案路徑 / markdown / 換行符號
    _raw_cta = ai_data.get("cta", "你怎麼看？")
    _cta_first_line = _raw_cta.split("\n")[0].split("\\n")[0].strip()
    # 若含有反引號（檔名標記）或太長，截短
    if "`" in _cta_first_line or len(_cta_first_line) > 40:
        _cta_first_line = _cta_first_line.split("`")[0].strip()
    question = _cta_first_line if _cta_first_line else "你怎麼看？"

    slide_idx = 1  # Track actual slide numbers for s00, s01, etc.

    # 1. 封面
    # 封面標題：直接用 hook，不拼接 what（避免長文截斷）
    # smart_title_lines 會自動依 max_per_line=10 分行
    hook_text = ai_data.get("hook", "最新快訊")
    cover_title = hook_text

    slide_hook(bgs[0], theme, cover_title,
               what_preview, f"{slide_idx} / {N}", p(slide_idx), person_mode=has_person)
    slide_idx += 1

    # ── HTML 渲染器（優先）+ PIL fallback ──
    _use_html = False
    try:
        from html_renderer import (render_keypoints, render_faq,
                                    render_analysis, render_ending, is_available)
        _use_html = is_available()
        if _use_html:
            print("   🎨 使用 HTML+CSS 渲染引擎（高品質模式）")
    except ImportError:
        pass

    accent = theme.get("accent", (247, 183, 49))
    accent_hex = '#%02x%02x%02x' % accent if isinstance(accent, tuple) else str(accent)
    watermark_name = theme.get("name_en", "CRYPTO NEWS")

    # 2. 核心要點
    kp_out = p(slide_idx)
    if _use_html:
        _html_ok = render_keypoints(
            raw_points[:4], accent_hex, f"{slide_idx} / {N}", kp_out,
            watermark=watermark_name)
        if not _html_ok:
            slide_keypoints_abmedia(bgs[1], theme, keypoint_texts, f"{slide_idx} / {N}", kp_out)
    else:
        slide_keypoints_abmedia(bgs[1], theme, keypoint_texts, f"{slide_idx} / {N}", kp_out)
    slide_idx += 1

    # 3-4. FAQ/分析頁（可能有多頁）
    if N >= 5:
        # 有額外的內容頁
        if has_rich_impact and len(impact_text) > 100:
            analysis_out = p(slide_idx)
            big_num = ai_data.get("big_number", "")
            mood_label = ai_data.get("mood", "")
            if _use_html:
                _html_ok = render_analysis(
                    "深度分析", impact_text[:400], accent_hex, f"{slide_idx} / {N}",
                    analysis_out, big_number=big_num, big_label=mood_label,
                    watermark=watermark_name)
                if not _html_ok:
                    slide_analysis_abmedia(bgs[2], theme, "深度分析", impact_text[:300],
                                          image=None, slide_info=f"{slide_idx} / {N}", out=analysis_out)
            else:
                slide_analysis_abmedia(bgs[2], theme, "深度分析", impact_text[:300],
                                      image=None, slide_info=f"{slide_idx} / {N}", out=analysis_out)
            slide_idx += 1

        # FAQ 頁
        if slide_idx < N:
            faq_out = p(slide_idx)
            if _use_html:
                _html_ok = render_faq(
                    faq_items, accent_hex, f"{slide_idx} / {N}", faq_out,
                    watermark=watermark_name)
                if not _html_ok:
                    slide_faq_abmedia(bgs[slide_idx - 1], theme, faq_items, f"{slide_idx} / {N}", faq_out)
            else:
                slide_faq_abmedia(bgs[slide_idx - 1], theme, faq_items, f"{slide_idx} / {N}", faq_out)
            slide_idx += 1
    else:
        # 4 頁版本：直接放 FAQ
        if bgs[2]:
            faq_out = p(slide_idx)
            if _use_html:
                _html_ok = render_faq(
                    faq_items, accent_hex, f"{slide_idx} / {N}", faq_out,
                    watermark=watermark_name)
                if not _html_ok:
                    slide_faq_abmedia(bgs[2], theme, faq_items, f"{slide_idx} / {N}", faq_out)
            else:
                slide_faq_abmedia(bgs[2], theme, faq_items, f"{slide_idx} / {N}", faq_out)
            slide_idx += 1

    # 最後：結尾頁
    last_idx = N - 1
    if last_idx >= 0 and bgs[last_idx]:
        ending_out = p(N)
        if _use_html:
            _html_ok = render_ending(
                question, brand_name, accent_hex, f"{N} / {N}", ending_out)
            if not _html_ok:
                slide_ending(bgs[last_idx], theme, question, brand_name, f"{N} / {N}", ending_out)
        else:
            slide_ending(bgs[last_idx], theme, question, brand_name, f"{N} / {N}", ending_out)

    return paths


def make_card(channel_type: str, title: str, content: str, output_path: str,
              source: str = "", article_url: str = ""):
    theme = THEMES.get(channel_type, THEMES["crypto"])
    palette = _pick_palette(title[:30])
    # 不覆蓋 theme accent，保持頻道固定色
    photo = get_photo(article_url, theme["keyword"], title[:20], 0)
    bg = make_background(photo, theme, palette=palette, slide_idx=0, article_seed=title[:30])
    slide_hook(bg, theme, title, content[:50], "1 / 1", output_path)
    return output_path


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IG 圖卡生成器 v4")
    parser.add_argument("--type", choices=["crypto", "finance", "startup"], default="crypto")
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--output", default="/tmp/ig_card.jpg")
    parser.add_argument("--article-url", default="")
    parser.add_argument("--carousel", action="store_true")
    parser.add_argument("--output-dir", default="/tmp/carousel/")
    args = parser.parse_args()

    if args.carousel:
        ai_data = {
            "hook":   args.title,
            "what":   args.content,
            "points": [f"重點一|{args.content[:40]}", "重點二|詳見連結", "重點三|追蹤不錯過"],
            "impact": args.content,
            "cta":    "你覺得呢？留言告訴我！",
        }
        paths = generate_carousel(args.type, ai_data, args.article_url,
                                  args.source, args.output_dir)
        print(json.dumps(paths, ensure_ascii=False))
    else:
        make_card(args.type, args.title, args.content, args.output,
                  args.source, args.article_url)
