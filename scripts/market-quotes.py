#!/usr/bin/env python3
"""
市場指數 + 黃金/白銀報價（固定資料源：Yahoo Finance）
背景：stooq.com/q/l/ CSV 端點已全面回 404，故改用 Yahoo Finance chart API。
報價格式依老闆 2026-08-04 指示：黃金/白銀一律「每盎司美元」。
"""
import datetime
import json
import urllib.request
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

SYMBOLS = [
    # 美股三大
    ("S&P 500", "^GSPC", "點"),
    ("Nasdaq", "^IXIC", "點"),
    ("Dow Jones", "^DJI", "點"),
    # 亞洲股市
    ("台股加權", "^TWII", "點"),
    ("恒生", "^HSI", "點"),
    ("日經225", "^N225", "點"),
    # 匯率 / 債息 / 恐慌指數
    ("USD/TWD", "TWD=X", "新台幣/美元"),
    ("美10年債息", "^TNX", "%"),
    ("VIX恐慌", "^VIX", "點"),
    ("美元指數", "DX-Y.NYB", "點"),
    # 商品（金銀油）
    ("黃金美元", "GC=F", "美元/盎司"),
    ("白銀美元", "SI=F", "美元/盎司"),
    ("原油WTI", "CL=F", "美元/桶"),
    ("原油Brent", "BZ=F", "美元/桶"),
    # 加密（若需要）
    ("Bitcoin", "BTC-USD", "美元"),
    ("Ethereum", "ETH-USD", "美元"),
]


def fetch(symbol):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           "?range=1mo&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    result = data["chart"]["result"][0]
    meta = result["meta"]
    price = meta.get("regularMarketPrice")

    # 前收 = 日線序列倒數第二筆（真正的上一個交易日收盤）。
    # 註：meta.chartPreviousClose 是「查詢區間之前」的收盤（range=5d 會拿到 5 天前的收盤），
    #     用它算漲跌幅會失真 —— 2026-10-25 修正。
    ts = result.get("timestamp") or []
    closes = (result.get("indicators", {}).get("quote", [{}])[0] or {}).get("close") or []
    series = [(t, c) for t, c in zip(ts, closes) if c is not None]
    prev = series[-2][1] if len(series) >= 2 else None

    asof = "?"
    if series:
        try:
            tz = ZoneInfo(meta.get("exchangeTimezoneName") or "UTC")
            asof = datetime.datetime.fromtimestamp(series[-1][0], tz).strftime("%Y-%m-%d")
        except Exception:
            asof = datetime.datetime.fromtimestamp(
                series[-1][0], datetime.timezone.utc).strftime("%Y-%m-%d")

    pct = (price - prev) / prev * 100 if (price and prev) else None
    return price, prev, pct, asof


def main():
    print("--- INDEX & METAL QUOTES (Yahoo Finance) ---")
    for label, symbol, unit in SYMBOLS:
        try:
            price, prev, pct, asof = fetch(symbol)
            if price is None:
                print(f"{label:12s} N/A (回傳無價格)")
                continue
            arrow = "" if pct is None else ("▲" if pct >= 0 else "▼")
            prev_s = f"{prev:,.2f}" if prev else "?"
            pct_s = f"{pct:+.2f}%" if pct is not None else "N/A"
            print(f"{label:12s} {price:>12,.2f} {unit:9s} 前收 {prev_s:>12s}  {arrow} {pct_s}  [{asof}]")
        except Exception as e:
            print(f"{label:12s} ERR {type(e).__name__}: {e}")
    print("--- END ---")


if __name__ == "__main__":
    main()
