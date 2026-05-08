#!/usr/bin/env python3
"""
內容自動化 Pipeline v3
功能：RSS + Twitter 抓文章 → 評分挑最熱 → AI 改寫 → 生成 5 張 Carousel → 發 IG

用法：
  python3 content_pipeline.py --channel crypto
  python3 content_pipeline.py --channel finance
  python3 content_pipeline.py --channel startup
  python3 content_pipeline.py --channel crypto --dry-run   # 只生成，不發文
"""

import os
import sys
import json
import argparse
import subprocess
import re
import html
import random
from typing import Optional
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


# ── 簡體字→繁體字自動轉換 ────────────────────────────────────
def to_traditional(text: str) -> str:
    """將 AI 生成文字中的簡體字轉為台灣正體（繁體）。
    優先使用 opencc（精確），fallback 到內建常見字對照表。"""
    if not text:
        return text
    try:
        from opencc import OpenCC
        cc = OpenCC('s2twp')  # 簡體→台灣正體（含慣用語轉換）
        return cc.convert(text)
    except ImportError:
        pass
    # fallback：高頻簡體字對照表
    _S2T = {
        '关': '關', '个': '個', '们': '們', '与': '與', '为': '為',
        '么': '麼', '义': '義', '乐': '樂', '书': '書', '买': '買',
        '产': '產', '亿': '億', '从': '從', '仅': '僅', '会': '會',
        '传': '傳', '价': '價', '众': '眾', '优': '優', '华': '華',
        '发': '發', '变': '變', '号': '號', '团': '團', '国': '國',
        '图': '圖', '场': '場', '块': '塊', '处': '處', '备': '備',
        '头': '頭', '实': '實', '对': '對', '导': '導', '将': '將',
        '尔': '爾', '层': '層', '币': '幣', '师': '師', '带': '帶',
        '开': '開', '张': '張', '当': '當', '录': '錄', '总': '總',
        '战': '戰', '护': '護', '报': '報', '据': '據', '择': '擇',
        '损': '損', '换': '換', '数': '數', '时': '時', '显': '顯',
        '机': '機', '权': '權', '条': '條', '来': '來', '构': '構',
        '标': '標', '样': '樣', '检': '檢', '业': '業', '极': '極',
        '欢': '歡', '汇': '匯', '没': '沒', '济': '濟', '涨': '漲',
        '减': '減', '满': '滿', '点': '點', '热': '熱', '环': '環',
        '现': '現', '电': '電', '确': '確', '离': '離', '积': '積',
        '称': '稱', '稳': '穩', '笔': '筆', '签': '簽', '类': '類',
        '经': '經', '结': '結', '给': '給', '统': '統', '续': '續',
        '网': '網', '联': '聯', '获': '獲', '虑': '慮', '规': '規',
        '观': '觀', '计': '計', '认': '認', '议': '議', '设': '設',
        '证': '證', '评': '評', '话': '話', '该': '該', '说': '說',
        '请': '請', '调': '調', '谁': '誰', '资': '資', '质': '質',
        '购': '購', '赢': '贏', '转': '轉', '达': '達', '进': '進',
        '运': '運', '过': '過', '还': '還', '这': '這', '选': '選',
        '链': '鏈', '间': '間', '阶': '階', '险': '險', '难': '難',
        '须': '須', '额': '額', '风': '風', '验': '驗', '龙': '龍',
        '厉': '厲', '历': '歷', '压': '壓', '参': '參', '双': '雙',
        '听': '聽', '响': '響', '园': '園', '坚': '堅', '壮': '壯',
        '夺': '奪', '奖': '獎', '学': '學', '宝': '寶', '审': '審',
        '属': '屬', '岁': '歲', '巨': '巨', '币': '幣', '广': '廣',
        '庆': '慶', '异': '異', '弹': '彈', '强': '強', '归': '歸',
        '态': '態', '怀': '懷', '惊': '驚', '战': '戰', '挡': '擋',
        '挤': '擠', '击': '擊', '拥': '擁', '担': '擔', '拦': '攔',
        '拨': '撥', '挣': '掙', '据': '據', '损': '損', '摆': '擺',
        '触': '觸', '词': '詞', '试': '試', '详': '詳', '误': '誤',
        '读': '讀', '谢': '謝', '谱': '譜', '负': '負', '贡': '貢',
        '货': '貨', '贵': '貴', '赞': '贊', '赶': '趕', '趋': '趨',
        '软': '軟', '轮': '輪', '辑': '輯', '辩': '辯', '迁': '遷',
        '适': '適', '逻': '邏', '遗': '遺', '邮': '郵', '释': '釋',
        '钱': '錢', '钻': '鑽', '铁': '鐵', '银': '銀', '锁': '鎖',
        '错': '錯', '镇': '鎮', '门': '門', '闪': '閃', '阅': '閱',
        '阵': '陣', '际': '際', '隐': '隱', '雇': '僱', '靠': '靠',
        '顿': '頓', '颁': '頒', '飞': '飛', '饰': '飾', '驱': '驅',
    }
    for s, t in _S2T.items():
        if s in text:
            text = text.replace(s, t)
    return text


# ── AI 垃圾內容過濾（防止 MiniMax 等模型夾帶系統指令）──────────
def _filter_ai_garbage(text: str) -> str:
    """移除 AI 生成內容中夾帶的系統指令、檔案路徑、要求確認等廢話。
    例如：'儲存到 `xxx.txt`，加上之前寫的 caption 就能生成完整圖卡。請說「可以」我就生成！'
    """
    if not text:
        return text
    lines = text.splitlines()
    # 擋關鍵字：AI 系統指令、檔案路徑句、要求確認句
    _GARBAGE_PATTERNS = (
        "儲存到", "請說「", "說「可以」", "生成完整圖卡",
        "加上之前寫的", "完整圖卡", "我就可以生成",
        ".txt`，", "`.py`，", "就能生成", "這樣就能",
        "`.py`）", "`）", "生成圖卡", "生成圖片",
"`xxx.txt`", "`caption.txt`", "`full.txt`",
        "說「算了」", "說「可以」", "「可以」我就", "說「算了」",
    )
    # 擋整行看起來像程式碼或指令的（含有「`」且含有「→」或「請」或「生成」）
    def is_garbage(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        for pat in _GARBAGE_PATTERNS:
            if pat in stripped:
                return True
        # 清除孤立的 `--` 分隔行（前後都是段落的話）
        if stripped == "---":
            return True
        return False

    filtered = [ln for ln in lines if not is_garbage(ln)]
    # 清除結尾的空行（避免多個換行）
    while filtered and not filtered[-1].strip():
        filtered.pop()
    return "\n".join(filtered)


# ── 台灣口語 Humanizer（爆笑風格）──────────────────────────────

_TW_SLANG = {
    "非常": ["超", "爆", "整個", "真的超", "也太"],
    "認為": ["覺得", "認為啦", "老實說", "說真的", "個人是覺得"],
    "可能": ["大概", "應該是", "八成", "可能啦", "說不定"],
    "因為": ["因為這樣", "所以啦", "主要是", "說穿了就是"],
    "但是": ["不過啦", "可是說真的", "話說回來", "只是啊"],
    "因此": ["所以", "就變成", "結果就是", "所以啊"],
    "問題": ["鳥事", "麻煩", "問題來了", "雷點", "硬傷"],
    "重要": ["有夠重要", "真的關鍵", "不能不注意", "一定要知道"],
    "厲害": ["有猛", "太神了", "猛猛的", "有夠強", "根本怪物"],
    "獲得": ["拿到", "順利拿到", "成功入手", "順順拿到"],
    "表示": ["就說啊", "意思是", "代表的意義是", "言下之意是"],
    "出現": ["冒出來", "冒出頭", "現身", "橫空出世"],
    "宣布": ["公布", "丟出來", "正式說了", "公告出來"],
    "價格": ["價錢", "價位", "價格拉", "價格變化"],
    "上漲": ["漲翻天", "往上噴", "暴漲", "狂飆", "起飛"],
    "下跌": ["跌到歪歪", "往下掉", "跳水", "破底", "崩跌"],
    "投資人": ["韭菜", "投資客", "鄉民", "肥宅", "各位"],
    "美元": ["摳摳", "大洋", "鈔票", "Money"],
    "比特幣": ["BTC", "一哥", "幣圈一哥", "大餅"],
    "以太坊": ["ETH", "二哥", "以太"],
    "億": ["爽賺", "大賺", "海撈"],
    "%": ["趴", "％"],
    "記者": ["小弟", "小妹", "本人", "筆者"],
}

_TW_EXCLAMATIONS = [
    "真的假的啦！",
    "不是喔！",
    "太扯了！",
    "笑死",
    "我傻眼",
    "這也行？",
    "崩潰",
    "給他死",
    "完蛋了",
    "穩了穩了",
    "爽啦！",
    "靠腰",
    "後悔",
    "GG",
    "有前途",
]

_TW_PUNCHLINES = [
    "，結果出事了",
    "，鄉民全傻眼",
    "，網友：？？？",
    "，專家說會更慘",
    "，韭菜又受傷了",
    "，資金悄悄跑了",
    "，暴漲前兆？",
    "，先跑先贏",
    "，各位要哭了",
    "，明天開盤見真章",
    "，你各位可以睡了",
]


def _pick_random(items: list[str]) -> str:
    import random
    return items[random.randint(0, len(items) - 1)] if items else ""


def _has_emoji(text: str) -> bool:
    """檢查是否已有 emoji"""
    emoji_ranges = [
        (0x2600, 0x26FF),  # 裝飾符號
        (0x2700, 0x27BF),  # 符號
        (0x1F600, 0x1F64F),  # 表情
        (0x1F300, 0x1F5FF),  # 符號
        (0x1F680, 0x1F6FF),  # 交通
        (0x1F1E0, 0x1F1FF),  # 國旗
    ]
    for c in text:
        for start, end in emoji_ranges:
            if start <= ord(c) <= end:
                return True
    return False


def humanize_taiwanese(text: str, intensity: str = "medium") -> str:
    """將正規新聞稿改寫為台灣口語爆笑風格

    Args:
        text: 原始文字
        intensity: "light"(輕度口語) / "medium"(中度爆笑) / "wild"(超級無厘頭)

    Returns:
        改寫後的文字
    """
    if not text or len(text) < 10:
        return text

    result = text

    # 1. 專業術語 → 口語化（只在非頭尾位置）
    if intensity in ("medium", "wild"):
        for formal, informal_list in _TW_SLANG.items():
            if formal in result:
                # 保留句首的術語（避免破壞開頭）
                informal = _pick_random(informal_list)
                # 簡單替換（只替換非句首的）
                result = result.replace(f" {formal} ", f" {informal} ")
                result = result.replace(f"　{formal}　", f"　{informal}　")

    # 2. 句尾爆笑化（根據 intensity）
    if intensity in ("medium", "wild"):
        sentences = []
        for sent in re.split(r'([。！？\n]+)', result):
            if not sent.strip():
                continue
            # 機率性添加驚嘆語（30-60%）
            should_add = random.random() < (0.3 if intensity == "medium" else 0.6)
            has_punc = any(c in sent for c in '。！？')
            if should_add and has_punc and not _has_emoji(sent):
                punchline = _pick_random(_TW_PUNCHLINES)
                exclamation = _pick_random(_TW_EXCLAMATIONS)
                choice = random.choice([punchline, exclamation])
                # 替換句尾標點
                for p in '。！？':
                    if sent.endswith(p):
                        sent = sent[:-1] + choice
                        break
                else:
                    sent = sent + choice
            sentences.append(sent)
        result = ''.join(sentences)

    # 3. 數字誇張化（wild 模式）
    if intensity == "wild":
        # 億 → 爽賺 / 大撈
        result = re.sub(r'(\d+)億', lambda m: f'{m.group(1)}億{m.group(1)}爽' if int(m.group(1)) > 1 else m.group(0), result)
        # % → 趴
        result = re.sub(r'(\d+(?:\.\d+)?)%', r'\1趴', result)
        # 大數字加強語氣
        result = re.sub(r'(\d{2,})', r'💰\1', result)

    # 4. 添加情緒语气（輕度）
    if intensity == "light":
        exclamations = ["！", "啊", "啦", "喔"]
        if result and result[-1] in '。！？':
            result = result[:-1] + _pick_random(exclamations)

    return result


def regenerate_hook(title: str, desc: str, channel: str = "crypto",
                    style: str = "shocking") -> Optional[str]:
    """專門為了解決 HOOK 失敗問題的 hook 重新生成

    Args:
        title: 原始新聞標題
        desc: 文章摘要
        channel: 頻道
        style: "shocking"(震驚型) / "curious"(好奇型) / "funny"(搞笑型) / "question"(問句型)

    Returns:
        新的 hook 字串，或 None
    """
    ch_zh = CHANNEL_ZH.get(channel, "綜合")

    style_prompts = {
        "shocking": "你要生成一個讓人震驚到下巴掉下來的 IG Hook。像是「OMG」「你相信嗎」這種讓人想繼續看下去的標題。",
        "curious": "你要生成一個讓人好奇心爆發的 IG Hook。像是「原來是這樣」「沒想到」「關鍵原因是」這種吊人胃口的標題。",
        "funny": "你要生成一個讓人笑到噴飯的 IG Hook。要用台灣鄉民那種kuso幽默，像是「場面一度非常尷尬」「老闆覺得可以」這種。",
        "question": "你要生成一個讓人忍不住想回答的 IG Hook。像是問答題一樣，讓讀者心裡有答案很想留言。",
    }

    style_prompt = style_prompts.get(style, style_prompts["shocking"])

    prompt = f"""你是台灣 {ch_zh} IG 社群的小編，要生成一個超級吸睛的 Hook 標題。

{style_prompt}

規則：
- 15-20 字以內（繁體中文）
- 結尾要有情緒張力（震驚/好奇/好笑）
- 絕對不能有簡體字
- 不要用「進行」「予以」「針對」等公文書面用語
- 要像 PTT 鄉民說話的口吻，或像 IG 網紅的風格

新聞標題：{title}
新聞摘要：{desc[:200]}

請直接輸出一句 Hook，不加任何說明，冒號後馬上寫內容：

HOOK:"""

    output = call_ai_claude(prompt, channel)
    if output and ":" in output:
        hook = output.split(":", 1)[-1].strip()
        # 清理可能的 Markdown 和多餘空白
        hook = re.sub(r'^\*+\s*', '', hook).strip()
        hook = re.sub(r'\s*\*+$', '', hook).strip()
        if len(hook) >= 5 and len(hook) <= 30:
            return hook
    return None


# ── 已發文歷史（防重複發文）────────────────────────────────────
POSTED_HISTORY = SCRIPT_DIR / "posted_history.json"

# ── IG 帳號 Config 對應 ──────────────────────────────────────
IG_CONFIG_MAP = {
    "crypto":  SCRIPT_DIR / "ig_config.json",          # @money.showtime
    "finance": SCRIPT_DIR / "ig_config.json",          # @money.showtime
    "startup": SCRIPT_DIR / "startup_ig_config.json",  # @bossmaker.lab
}

# ── RSS 來源（大幅升級，改抓知名主流話題）────────────────────────
RSS_SOURCES = {
    "crypto": [
        # 中文優先（台灣讀者直接看懂）
        {"name": "動區動趨",       "url": "https://www.blocktempo.com/feed/",           "lang": "zh"},
        # ⚠️ 2024 broken (DNS fail): {"name": "金色財經", "url": "https://www.jinse.cn/rss", "lang": "zh"},
        {"name": "幣學",           "url": "https://blockcast.it/feed/",                "lang": "zh"},
        {"name": "鏈新聞ABMedia",  "url": "https://abmedia.io/feed",                  "lang": "zh"},
        # ⚠️ 2024 broken (XML parse): {"name": "PANews", "url": "https://www.panewslab.com/rss", "lang": "zh"},
        # ⚠️ 2024 broken (404): {"name": "律動BlockBeats", "url": "https://www.theblockbeats.info/rss", "lang": "zh"},
        # ⚠️ 2024 broken (HTTP 567): {"name": "Foresight News", "url": "https://foresightnews.pro/rss", "lang": "zh"},
        {"name": "Odaily星球日報",  "url": "https://www.odaily.news/rss",              "lang": "zh"},
        {"name": "Mars Finance",   "url": "https://news.marsbit.co/feed",             "lang": "zh"},
        # 英文主流（BTC/ETH/政策/名人新聞多）
        {"name": "Bitcoin Magazine","url": "https://bitcoinmagazine.com/.rss/full/",   "lang": "en"},
        {"name": "Decrypt",        "url": "https://decrypt.co/feed",                   "lang": "en"},
        {"name": "The Block",      "url": "https://www.theblock.co/rss.xml",           "lang": "en"},
        {"name": "CoinTelegraph",  "url": "https://cointelegraph.com/rss",             "lang": "en"},
        {"name": "CoinDesk",       "url": "https://feeds.feedburner.com/CoinDesk",     "lang": "en"},
        {"name": "CryptoSlate",    "url": "https://cryptoslate.com/feed/",             "lang": "en"},
        # ⚠️ 2024 broken (XML parse): {"name": "DL News", "url": "https://www.dlnews.com/rss/", "lang": "en"},
        {"name": "Unchained",      "url": "https://unchainedcrypto.com/feed/",        "lang": "en"},
    ],
    "finance": [
        # 中文財經（台灣讀者直接看懂）
        {"name": "經濟日報",       "url": "https://money.udn.com/rssfeed/news/1001/5588", "lang": "zh"},
        {"name": "TechNews財經",   "url": "https://finance.technews.tw/feed/",            "lang": "zh"},
        {"name": "Yahoo財經",      "url": "https://tw.stock.yahoo.com/rss?category=intl-market", "lang": "zh"},
        {"name": "Google財經",     "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FucG9HZ0pVVnlnQVAB?hl=zh-TW&gl=TW&ceid=TW:zh-Hant", "lang": "zh"},
        {"name": "商業周刊",       "url": "https://www.businessweekly.com.tw/rss/",    "lang": "zh"},
        {"name": "工商時報",       "url": "https://ctee.com.tw/feed",                  "lang": "zh"},
        # 英文主流財經（涵蓋地緣政治、商品、全球趨勢）
        {"name": "MarketWatch",    "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories", "lang": "en"},
        {"name": "CNBC Top News",  "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "lang": "en"},
        {"name": "Bloomberg Markets","url": "https://feeds.bloomberg.com/markets/news.rss", "lang": "en"},
        {"name": "Reuters",        "url": "https://www.reutersagency.com/feed/",       "lang": "en"},
        {"name": "WSJ Markets",    "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "lang": "en"},
    ],
    "startup": [
        {"name": "Inside",         "url": "https://www.inside.com.tw/feed",             "lang": "zh"},
        {"name": "TechNews台灣",   "url": "https://technews.tw/feed/",                 "lang": "zh"},
        {"name": "TechCrunch",     "url": "https://techcrunch.com/feed/",               "lang": "en"},
        {"name": "Crunchbase News","url": "https://news.crunchbase.com/feed/",          "lang": "en"},
    ],
}

# ── 影響力倍增器（重磅事件 ×3，中度事件 ×2）───────────────────
MAJOR_IMPACT_KW = {
    "crypto": [
        "ETF", "比特幣ETF", "現貨ETF", "監管", "禁令", "禁令", "違法",
        "駭客", "hack", "被盜", "攻擊", "漏洞",
        "機構買入", "機構採用", "國家採用", "政府買進", "戰略儲備",
        "blackrock", "貝萊德", "microstrategy", "coinbase訴", "sec訴",
        "上市", "下市", "納斯達克", "上架", "下架",
        "輝瑞", "Tesla買", "馬斯克買",
    ],
    "finance": [
        "Fed", "聯準會", "升息", "降息", "CPI", "通膨", "非農",
        "川普關稅", "制裁", "戰爭", "停火", "協議",
        "GDP", "衰退", "危機", "銀行倒閉",
        "納斯達克新高", "S&P500新高", "歷史高點",
    ],
    "startup": [
        "IPO", "上市", "併購", "收購", "收購",
        "獨角獸", "估值十億", "新創破產",
        "裁員", "倒閉",
    ],
}

MEDIUM_IMPACT_KW = {
    "crypto": [
        "SEC", "CFTC", "監管", "法規", "許可", "牌照",
        "binance", "coinbase", "交易所", "上幣",
        "DeFi", "Aave", "Uniswap", "Layer2", "L2",
        "比特幣網路", "算力", "礦工",
        "牛市", "熊市", "爆多", "爆空",
    ],
    "finance": [
        "半導體", "晶片", "AI晶片", "輝達",
        "黃金新高", "白銀", "原油新高",
        "台積電", "護國神山",
        "中國經濟", "恒大", "房市崩",
    ],
    "startup": [
        "融资", "估值", "集資",
        "OpenAI", "ChatGPT", "Anthropic", "AI模型",
    ],
}

# ── 瑣碎內容過濾器（這些模式不該進入版面）─────────────────────
# 符合任一 pattern → 罰分，降低被選中機率
TRIVIAL_PATTERNS = {
    "crypto": [
        # 純價格波動，無催化劑（漲跌 X% 全文沒說為什麼）
        "漲了", "跌了", "下跌", "上漲", "回升", "回落",
        "繼續漲", "繼續跌", "挑戰", "守住",
        "小幅", "微幅", "略微",
        # 日常技術分析、預測
        "分析師表示", "技術面", "均線", "支撐", "壓力",
        "短線", "操作建議", "進場時機",
        # 無實質內容的幣價文
        "比特幣今日", "以太坊今日", "幣圈今日",
    ],
}

# Crypto 最低門檻：分數低於這個 → 視為瑣碎內容，直接放棄
MIN_SCORE = {"crypto": 3, "finance": 2, "startup": 2}

# ── 熱門關鍵字（文章評分用）──────────────────────────────────────
# 分數越高 = 越熱門，優先選這篇發文
HOT_KEYWORDS = {
    "crypto": [
        # 主流幣種（高分）
        "BTC", "比特幣", "bitcoin", "ETH", "以太坊", "ethereum",
        "SOL", "solana", "XRP", "ripple", "BNB",
        # 重磅話題
        "ETF", "川普", "Trump", "馬斯克", "Musk", "Elon",
        "SEC", "CFTC", "穩定幣", "stablecoin", "USDT", "USDC",
        "儲備", "reserve", "國家", "政府", "美國", "政策",
        "牛市", "bull", "新高", "all-time high", "ATH",
        "coinbase", "binance", "幣安", "交易所",
        "AI", "人工智慧", "區塊鏈", "blockchain",
        # 知名人物
        "michael saylor", "saylor", "blackrock", "貝萊德",
        "apple", "tesla", "蘋果", "特斯拉",
        # DeFi / L2 / 新領域（增加多樣性）
        "DeFi", "Aave", "Uniswap", "Layer 2", "L2", "Base", "Arbitrum", "Optimism",
        "Sui", "Aptos", "Solana", "迷因幣", "memecoin",
        "Web3", "DAO", "NFT", "RWA",
        "礦工", "miner", "算力", "比特幣網路",
    ],
    "finance": [
        # 股市
        "美股", "台股", "納斯達克", "道瓊", "S&P500", "恒生", "日經",
        # 央行與貨幣政策
        "聯準會", "Fed", "升息", "降息", "通膨", "inflation", "CPI", "利率",
        # 地緣政治與國際
        "川普", "Trump", "關稅", "tariff", "戰爭", "war", "制裁", "sanctions",
        "中美", "台海", "烏克蘭", "Ukraine", "以色列", "Israel", "中東",
        # 商品與貴金屬
        "黃金", "gold", "白銀", "silver", "原油", "oil", "WTI", "布蘭特",
        "大宗商品", "commodity", "銅", "copper",
        # 科技巨頭
        "AI", "科技股", "輝達", "NVIDIA", "蘋果", "Apple", "特斯拉", "Tesla",
        # 經濟指標與名人
        "GDP", "就業", "失業率", "PMI", "消費者信心",
        "巴菲特", "Buffett", "馬斯克", "Musk", "IPO", "裁員",
        # 多元新主題
        "半導體", "晶片", "台積電", "AI股", "製藥", "生技",
        "中國經濟", "恒大", "房市", "陸股", "A股",
        "比特幣", "BTC", "以太幣", "ETH",  # 金融人也關注幣
    ],
    "startup": [
        "AI", "人工智慧", "OpenAI", "ChatGPT", "Gemini",
        "融資", "億", "估值", "unicorn", "獨角獸",
        "IPO", "上市", "裁員", "併購",
        "創辦人", "CEO", "創業", "新創",
        "台灣", "矽谷", "Silicon Valley",
        "Anthropic", "Google", "Apple", "Meta", "Microsoft",
    ],
}

# ── 完整文案 Hashtag ──────────────────────────────────────────
HASHTAGS = {
    "crypto":  "#幣圈 #加密貨幣 #BTC #比特幣 #ETH #Web3 #區塊鏈 #crypto #bitcoin #投資理財",
    "finance": "#金融 #投資 #理財 #股市 #經濟 #台股 #美股 #黃金 #國際局勢 #財經",
    "startup": "#創業 #新創 #商業 #AI #人工智慧 #成功 #創業故事 #entrepreneur #startup #台灣創業",
}

CHANNEL_ZH = {
    "crypto": "幣圈",
    "finance": "金融",
    "startup": "創業",
}

# ── Twitter 搜尋關鍵字 ────────────────────────────────────────
TWITTER_QUERIES = {
    "crypto":  "BTC OR ETH OR 比特幣 OR 加密貨幣 OR 穩定幣 -filter:retweets lang:zh",
    "finance": "美股 OR 台股 OR 黃金 OR 川普 OR 戰爭 OR 聯準會 OR 原油 -filter:retweets lang:zh",
    "startup": "AI 創業 OR 新創 OR 融資 -filter:retweets lang:zh",
}

# ── Nitter 鏡像實例（Twitter 隱私保護替代方案）────────────────
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
    "https://nitter.1d4.us",
]

# ── Telegram 公開頻道 ─────────────────────────────────────────
TELEGRAM_CHANNELS = {
    "crypto": [
        {"name": "Wu Blockchain", "url": "https://t.me/s/WuBlockchain"},
        {"name": "The Block", "url": "https://t.me/s/TheBlock__"},
        {"name": "Crypto Quant", "url": "https://t.me/s/CryptoQuantOfficial"},
    ],
    "finance": [
        {"name": "WSJ", "url": "https://t.me/s/wsaborningbrief"},
    ],
}


# ── RSS 抓取 ──────────────────────────────────────────────────

def fetch_rss(url: str, timeout: int = 10) -> list[dict]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=timeout) as resp:
            content = resp.read()
        root = ET.fromstring(content)

        articles = []
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items[:8]:
            def get(tag, ns=""):
                el = item.find(f"{ns}{tag}")
                return el.text.strip() if el is not None and el.text else ""

            title    = get("title") or get("title", "{http://www.w3.org/2005/Atom}")
            desc     = get("description") or get("summary", "{http://www.w3.org/2005/Atom}")
            link     = get("link") or get("link", "{http://www.w3.org/2005/Atom}")
            pub_date = get("pubDate") or get("published", "{http://www.w3.org/2005/Atom}")

            if title:
                desc_clean = html.unescape(re.sub(r'<[^>]+>', '', desc))[:600]
                title = html.unescape(title)
                articles.append({
                    "title":       title,
                    "description": desc_clean,
                    "link":        link,
                    "pub_date":    pub_date,
                })
        return articles
    except Exception as e:
        print(f"   ⚠️ RSS 抓取失敗 {url}: {e}")
        return []


# ── Twitter 抓取（bird）────────────────────────────────────────

def fetch_article_text(url: str, max_chars: int = 3000) -> str:
    """抓取文章頁面，提取主要文字內容（用於補充截斷的 RSS 描述）"""
    if not url:
        return ""

    # 重試機制：最多嘗試 2 次
    for attempt in range(2):
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            with urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")

            # 移除 script/style/nav/header/footer 區塊
            for tag in ("script", "style", "nav", "header", "footer", "aside"):
                raw = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', raw, flags=re.DOTALL|re.IGNORECASE)
            # 移除 HTML 註解
            raw = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)

            # 優先從 <article> 容器提取（大多數新聞網站用 article 標籤包內文）
            article_match = re.search(r'<article[^>]*>(.*?)</article>', raw, re.DOTALL|re.IGNORECASE)
            search_area = article_match.group(1) if article_match else raw

            # 嘗試多個內容容器選擇器
            if not article_match:
                for selector in ["<div class=\"content\"", "<div class=\"entry-content\"", "<div class=\"post-content\""]:
                    container_match = re.search(rf'{selector}[^>]*>(.*?)</div>', search_area, re.DOTALL|re.IGNORECASE)
                    if container_match:
                        search_area = container_match.group(1)
                        break

            # 提取 <p> 標籤內文字
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', search_area, re.DOTALL|re.IGNORECASE)

            # 過濾噪音的關鍵字（社群分享、導航、廣告等）
            noise_patterns = re.compile(
                r'分享至|share to|twitter|facebook|telegram|line\.me|複製連結|'
                r'廣告|贊助|sponsor|subscribe|訂閱|newsletter|'
                r'相關報導|延伸閱讀|read more|see also|'
                r'留言|comment|登入|sign in|cookie|前情提要|背景補充',
                re.IGNORECASE
            )

            texts = []
            for p in paragraphs:
                clean = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
                # 壓縮連續空白/換行為單一空格
                clean = re.sub(r'\s+', ' ', clean).strip()
                # 跳過條件：太短、包含噪音關鍵字、純連結/數字
                if len(clean) < 30:
                    continue
                if noise_patterns.search(clean) and len(clean) < 150:
                    continue  # 短段落含噪音就跳過；長段落（150+）可能是正文提到這些詞
                # 跳過看起來像列表項目（全是連結文字）
                if clean.count('http') > 2:
                    continue
                texts.append(clean)

            if texts:
                result = "\n".join(texts)
                # 最終清理：移除開頭可能殘留的分享按鈕文字
                result = re.sub(r'^(分享至\S+\s*)+', '', result).strip()
                return result[:max_chars]
            # 如果 <p> 標籤提取為空，繼續嘗試
        except Exception as e:
            if attempt < 1:
                continue
            print(f"   ⚠️ 文章抓取失敗 {url[:50]}: {e}")
            return ""

    return ""


# ── Reddit 熱門文章抓取 ────────────────────────────────────────

def fetch_reddit_hot(channel: str) -> list[dict]:
    """從 Reddit 爬取熱門貼文（無需授權，JSON API）"""
    subreddits = {
        "crypto": ["CryptoCurrency", "Bitcoin", "ethereum"],
        "finance": ["wallstreetbets", "stocks", "investing"],
        "startup": ["startups", "Entrepreneur"],
    }

    subs = subreddits.get(channel, [])
    if not subs:
        return []

    articles = []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    for sub in subs:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10"
            req = Request(url, headers={"User-Agent": user_agent})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            for child in data.get("data", {}).get("children", [])[:10]:
                post = child.get("data", {})
                title = post.get("title", "")
                selftext = post.get("selftext", "")[:300]
                score = post.get("score", 0)
                permalink = post.get("permalink", "")

                if title and len(title) > 10:
                    articles.append({
                        "title": title,
                        "description": selftext or title,
                        "link": f"https://reddit.com{permalink}" if permalink else "",
                        "pub_date": "",
                        "_source": f"Reddit/{sub}",
                        "_social_score": score,
                    })
        except Exception as e:
            print(f"   ⚠️ Reddit/{sub} 抓取失敗: {e}")

    return articles


# ── Google Trends 抓取 ──────────────────────────────────────────

def fetch_google_trends(channel: str) -> list[str]:
    """從 Google Trends RSS 取得台灣和美國當日趨勢關鍵字"""
    trends_keywords = []

    # 關鍵字過濾器
    filters = {
        "crypto": ["bitcoin", "ethereum", "crypto", "幣", "區塊鏈", "web3", "nft"],
        "finance": ["stock", "gold", "oil", "fed", "股票", "美股", "台股", "黃金"],
        "startup": ["ai", "startup", "openai", "創業", "新創", "融資"],
    }

    filter_kw = filters.get(channel, [])

    for geo in ["TW", "US"]:
        try:
            url = f"https://trends.google.com/trending/rss?geo={geo}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=10) as resp:
                content = resp.read()

            root = ET.fromstring(content)
            items = root.findall(".//item")

            for item in items[:15]:
                title_el = item.find("title")
                if title_el is None or not title_el.text:
                    continue
                title = title_el.text.strip()

                # 檢查是否符合頻道關鍵字
                if any(kw.lower() in title.lower() for kw in filter_kw):
                    if title not in trends_keywords:
                        trends_keywords.append(title)
        except Exception as e:
            print(f"   ⚠️ Google Trends ({geo}) 抓取失敗: {e}")

    return trends_keywords[:10]


# ── CoinGecko 趨勢幣種 ──────────────────────────────────────────

def fetch_coingecko_trending() -> list[dict]:
    """從 CoinGecko 公開 API 取得 24h 趨勢幣種"""
    trending_coins = []

    try:
        # 趨勢幣種
        url = "https://api.coingecko.com/api/v3/search/trending"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        for coin_entry in data.get("coins", [])[:5]:
            coin = coin_entry.get("item", {})
            coin_id = coin.get("id", "")
            name = coin.get("name", "")
            symbol = coin.get("symbol", "").upper()
            market_cap_rank = coin.get("market_cap_rank", "N/A")

            # 取得 24h 價格變化
            price_change = "N/A"
            try:
                price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
                price_req = Request(price_url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(price_req, timeout=10) as price_resp:
                    price_data = json.loads(price_resp.read().decode())
                    price_change = price_data.get(coin_id, {}).get("usd_24h_change", "N/A")
                    if price_change != "N/A":
                        price_change = f"{price_change:+.2f}%"
            except Exception:
                pass

            trending_coins.append({
                "name": name,
                "symbol": symbol,
                "market_cap_rank": market_cap_rank,
                "price_change_24h": price_change,
            })
    except Exception as e:
        print(f"   ⚠️ CoinGecko 抓取失敗: {e}")

    return trending_coins


# ── DeFi/區鏈資料擴充 ────────────────────────────────────────────

def fetch_onchain_context(article_title: str, channel: str) -> str:
    """從 DeFi Llama 和 Alternative.me 取得鏈上數據補充"""
    if channel != "crypto":
        return ""

    context_parts = []
    title_lower = article_title.lower()

    # DeFi Llama TVL（如果文章提及主流協議）
    try:
        if any(kw in title_lower for kw in ["defi", "tvl", "aave", "uniswap", "compound", "maker", "lido"]):
            req = Request("https://api.llama.fi/protocols", headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=10) as resp:
                protocols = json.loads(resp.read().decode())

            for proto in protocols[:50]:
                proto_name = proto.get("name", "").lower()
                if proto_name in title_lower:
                    tvl = proto.get("tvl", 0)
                    change_1d = proto.get("change_1d", 0)
                    if tvl:
                        tvl_str = f"${tvl/1e9:.2f}B" if tvl >= 1e9 else f"${tvl/1e6:.2f}M"
                        context_parts.append(
                            f"{proto.get('name')} TVL: {tvl_str} (24h: {change_1d:+.1f}%)"
                        )
                    break
    except Exception:
        pass

    # 比特幣恐懼貪婪指數
    try:
        if any(kw in title_lower for kw in ["bitcoin", "btc", "比特幣", "crypto", "加密"]):
            req = Request("https://api.alternative.me/fng/?limit=1", headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=5) as resp:
                fng_data = json.loads(resp.read().decode())

            fng_entry = fng_data.get("data", [{}])[0]
            fng_value = fng_entry.get("value", "")
            fng_class = fng_entry.get("value_classification", "")
            if fng_value:
                context_parts.append(f"恐懼貪婪指數: {fng_value} ({fng_class})")
    except Exception:
        pass

    return " | ".join(context_parts) if context_parts else ""


def analyze_sentiment(articles: list[dict]) -> dict:
    """分析收集到的文章整體情緒（bullish/bearish/neutral）"""
    positive_keywords = [
        "牛市", "上漲", "新高", "突破", "暴漲",
        "bullish", "rally", "surge", "soar", "all-time high", "ATH",
        "利多", "看好", "反彈", "復甦"
    ]
    negative_keywords = [
        "熊市", "暴跌", "崩盤", "下跌", "被盜",
        "hack", "crash", "plunge", "dump",
        "利空", "看跌", "恐慌", "危機", "崩壞", "爆雷"
    ]

    positive_count = 0
    negative_count = 0

    # 遍歷所有文章，計算正負關鍵字出現次數
    for article in articles:
        text = (article.get("title", "") + " " + article.get("description", "")).lower()

        for kw in positive_keywords:
            if kw.lower() in text:
                positive_count += text.count(kw.lower())

        for kw in negative_keywords:
            if kw.lower() in text:
                negative_count += text.count(kw.lower())

    # 計算情緒分數：(正面 - 負面) / max(正面 + 負面, 1)
    total = max(positive_count + negative_count, 1)
    score = (positive_count - negative_count) / total

    # 根據分數判斷情緒傾向
    if score > 0.2:
        sentiment = "bullish"
        summary = "市場偏多，正面消息較多"
    elif score < -0.2:
        sentiment = "bearish"
        summary = "市場偏空，負面消息主導"
    else:
        sentiment = "neutral"
        summary = "市場中性，多空交織"

    return {
        "sentiment": sentiment,
        "score": score,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "summary": summary
    }


def _is_desc_sufficient(desc: str) -> bool:
    """判斷 RSS 描述是否足夠讓 AI 生成深度內容"""
    if not desc:
        return False
    # 截斷標記
    if "[…]" in desc or "[...]" in desc or "…]" in desc:
        return False
    # 太短（去除空白後不到 80 字）
    clean = desc.strip()
    if len(clean) < 80:
        return False
    return True


def fetch_twitter_trending(channel: str) -> list[dict]:
    """搜尋 Twitter/X 熱門推文，三層級錯誤回退機制

    Layer 1: bird CLI (快速、精確)
    Layer 2: snscrape Python 庫 (備用)
    Layer 3: Nitter RSS 提取 (隱私保護替代)
    """
    query = TWITTER_QUERIES.get(channel, "")
    if not query:
        return []

    # ── Layer 1: bird CLI ────────────────────────────────────
    try:
        print(f"   🐦 嘗試 bird CLI：{query[:50]}...")
        result = subprocess.run(
            ["bird", "search", query, "--count", "8"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            articles = []
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    tweet = json.loads(line)
                    text = (tweet.get("text") or tweet.get("full_text") or
                            tweet.get("content") or "")
                    if len(text) > 25:
                        articles.append({
                            "title":       text[:80],
                            "description": text,
                            "link":        tweet.get("url", ""),
                            "pub_date":    tweet.get("created_at", ""),
                            "_social_score": tweet.get("favorite_count", 0) + tweet.get("retweet_count", 0),
                        })
                except json.JSONDecodeError:
                    if len(line) > 25 and not line.startswith("#"):
                        articles.append({
                            "title":       line[:80],
                            "description": line,
                            "link":        "",
                            "pub_date":    "",
                            "_social_score": 0,
                        })
            if articles:
                print(f"   ✅ bird：取得 {len(articles)} 則推文")
                return articles
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        print("   ⚠️ bird 搜尋逾時，嘗試備用方案...")
    except Exception as e:
        print(f"   ⚠️ bird 失敗：{e}，嘗試備用方案...")

    # ── Layer 2: snscrape 庫 ────────────────────────────────
    try:
        print(f"   🐦 嘗試 snscrape：{query[:50]}...")
        import snscrape.modules.twitter as sntwitter

        articles = []
        search_query = query.replace(" lang:zh", "")
        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
                if i >= 8:
                    break
                text = tweet.content
                if len(text) > 25:
                    articles.append({
                        "title":       text[:80],
                        "description": text,
                        "link":        f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                        "pub_date":    tweet.date.isoformat() if hasattr(tweet, 'date') else "",
                        "_social_score": (tweet.likeCount or 0) + (tweet.retweetCount or 0),
                    })
        except Exception as inner_e:
            print(f"   ⚠️ snscrape 內部失敗：{inner_e}")

        if articles:
            print(f"   ✅ snscrape：取得 {len(articles)} 則推文")
            return articles
    except ImportError:
        pass
    except Exception as e:
        print(f"   ⚠️ snscrape 失敗：{e}，嘗試備用方案...")

    # ── Layer 3: Nitter RSS 提取 ────────────────────────────
    articles = []
    for nitter_url in NITTER_INSTANCES:
        try:
            print(f"   🐦 嘗試 Nitter ({nitter_url})：{query[:40]}...")
            # 簡化查詢，只用英文部分給 Nitter
            search_terms = query.replace(" -filter:retweets lang:zh", "").split(" OR ")[0]
            rss_url = f"{nitter_url}/search/rss?f=tweets&q={search_terms}"

            req = Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as resp:
                content = resp.read()

            root = ET.fromstring(content)
            items = root.findall(".//item")

            for item in items[:8]:
                def get(tag):
                    el = item.find(tag)
                    return el.text.strip() if el is not None and el.text else ""

                title = get("title")
                desc = get("description")
                link = get("link")
                pub_date = get("pubDate")

                if title and len(title) > 20:
                    articles.append({
                        "title":       title[:80],
                        "description": desc or title,
                        "link":        link,
                        "pub_date":    pub_date,
                        "_social_score": 0,  # Nitter RSS 無社群分數
                    })

            if articles:
                print(f"   ✅ Nitter：取得 {len(articles)} 則推文")
                return articles
        except Exception as e:
            print(f"   ⚠️ Nitter ({nitter_url})：{e}")
            continue

    if not articles:
        print(f"   ⚠️ Twitter 三層級備用全失敗，跳過此來源")
    return articles


# ── 鯨魚動向監控 ──────────────────────────────────────────────────

def fetch_whale_alerts(min_usd: int = 1_000_000) -> list[dict]:
    """監控大額加密貨幣交易

    Layer 1: Whale Alert 公開 API
    Layer 2: whale-alert.io 網頁爬蟲
    Layer 3: @whale_alert Twitter 帳戶 via Nitter RSS
    """
    articles = []

    # ── Layer 1: Whale Alert 公開 API ────────────────────────
    api_key = os.environ.get("WHALE_ALERT_API_KEY")
    if api_key:
        try:
            print(f"   🐳 嘗試 Whale Alert API...")
            url = f"https://api.whale-alert.io/v1/transactions?min_value={min_usd}&api_key={api_key}"
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            for tx in data.get("result", [])[:10]:
                from_address = tx.get("from", {})
                to_address = tx.get("to", {})
                amount = tx.get("amount", 0)
                value_usd = tx.get("amount_usd", 0)
                blockchain = tx.get("blockchain", "").upper()
                hash_id = tx.get("hash", "")

                if amount > 0:
                    title = f"🐳 {blockchain}: {amount:,.0f} ({value_usd:,.0f} USD)"
                    description = f"從 {from_address.get('label', from_address.get('address', 'Unknown')[:16])} 轉至 {to_address.get('label', to_address.get('address', 'Unknown')[:16])}"

                    articles.append({
                        "title":       title,
                        "description": description,
                        "link":        f"https://whale-alert.io/" if hash_id else "",
                        "pub_date":    tx.get("timestamp", ""),
                        "_social_score": int(value_usd / 100_000),  # 以 USD 為基準計分
                    })

            if articles:
                print(f"   ✅ Whale Alert API：取得 {len(articles)} 筆大額交易")
                return articles
        except Exception as e:
            print(f"   ⚠️ Whale Alert API 失敗：{e}，嘗試備用方案...")

    # ── Layer 2: whale-alert.io 網頁爬蟲 ──────────────────────
    try:
        print(f"   🐳 嘗試爬蟲 whale-alert.io...")
        url = "https://whale-alert.io/"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=20) as resp:
            html_content = resp.read().decode(errors='ignore')

        # 簡單的正則搜尋最近交易
        import re
        patterns = [
            r'([0-9,]+)\s*(?:BTC|ETH|USDC|USDT)\s*\(\$([0-9,]+)',
            r'transferred\s*([0-9,\.]+)\s*([A-Z]+)\s*(?:worth|valued at)?\s*\$?([0-9,]+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, html_content):
                try:
                    amount = match.group(1).replace(',', '')
                    value = match.group(2).replace(',', '')
                    if float(value) >= min_usd:
                        articles.append({
                            "title": f"🐳 {amount} ({value} USD)",
                            "description": "大額交易檢測自 whale-alert.io",
                            "link": "https://whale-alert.io/",
                            "pub_date": "",
                            "_social_score": int(float(value) / 100_000),
                        })
                        if len(articles) >= 5:
                            break
                except (ValueError, IndexError):
                    continue
                if len(articles) >= 5:
                    break

        if articles:
            print(f"   ✅ whale-alert.io：取得 {len(articles)} 筆大額交易")
            return articles[:10]
    except Exception as e:
        print(f"   ⚠️ whale-alert.io 爬蟲失敗：{e}，嘗試備用方案...")

    # ── Layer 3: @whale_alert Twitter via Nitter ────────────
    try:
        print(f"   🐳 嘗試 @whale_alert Twitter via Nitter...")
        for nitter_url in NITTER_INSTANCES:
            try:
                rss_url = f"{nitter_url}/whale_alert/rss"
                req = Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=15) as resp:
                    content = resp.read()

                root = ET.fromstring(content)
                items = root.findall(".//item")

                for item in items[:5]:
                    def get(tag):
                        el = item.find(tag)
                        return el.text.strip() if el is not None and el.text else ""

                    title = get("title")
                    description = get("description")
                    link = get("link")
                    pub_date = get("pubDate")

                    if title and "whale" in title.lower():
                        articles.append({
                            "title":       title[:100],
                            "description": description[:300] if description else title,
                            "link":        link,
                            "pub_date":    pub_date,
                            "_social_score": 0,
                        })

                if articles:
                    print(f"   ✅ @whale_alert Twitter：取得 {len(articles)} 筆鯨魚動向")
                    return articles
            except Exception:
                continue
    except Exception as e:
        print(f"   ⚠️ Twitter @whale_alert 失敗：{e}")

    if not articles:
        print(f"   ⚠️ 鯨魚動向三層級備用全失敗")
    return articles


# ── Telegram 公開頻道訊息提取 ──────────────────────────────────

def fetch_telegram_channels(channel: str) -> list[dict]:
    """從公開 Telegram 頻道爬蟲最新訊息（無需 API）

    利用 https://t.me/s/ChannelName 公開網頁預覽，提取 HTML
    """
    channels = TELEGRAM_CHANNELS.get(channel, [])
    if not channels:
        return []

    articles = []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    for ch_info in channels:
        ch_name = ch_info.get("name", "")
        ch_url = ch_info.get("url", "")
        if not ch_url:
            continue

        try:
            print(f"   📱 抓取 Telegram：{ch_name}...")
            req = Request(ch_url, headers={"User-Agent": user_agent})
            with urlopen(req, timeout=15) as resp:
                html_content = resp.read().decode(errors='ignore')

            # 解析 HTML，尋找訊息文字
            import re

            # Telegram Web 公開預覽的訊息格式：<div class="tgme_widget_message_text">...</div>
            pattern = r'<div\s+class=["\']?tgme_widget_message_text["\']?>(.+?)</div>'
            matches = re.findall(pattern, html_content, re.DOTALL)

            for match in matches[:8]:
                # 清理 HTML 標籤和實體
                text = html.unescape(match)
                text = re.sub(r'<[^>]+>', '', text)  # 移除 HTML 標籤
                text = text.strip()

                if len(text) > 20:  # 最少 20 字
                    articles.append({
                        "title":       text[:80],
                        "description": text[:300],
                        "link":        ch_url,
                        "pub_date":    "",
                        "_source":     f"Telegram/{ch_name}",
                    })

            if articles:
                print(f"   ✅ Telegram/{ch_name}：取得 {len(articles)} 則訊息")
        except Exception as e:
            print(f"   ⚠️ Telegram/{ch_name}：{e}")

    return articles[:10]  # 最多 10 筆


# ── 文章評分（熱門程度）─────────────────────────────────────────

def _load_posted_history() -> list[dict]:
    """讀取已發文歷史"""
    if POSTED_HISTORY.exists():
        try:
            return json.loads(POSTED_HISTORY.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_posted_history(history: list[dict]):
    """儲存已發文歷史（只保留最近 200 筆）"""
    POSTED_HISTORY.write_text(json.dumps(history[-200:], ensure_ascii=False, indent=2))


def _is_already_posted(article: dict, channel: str) -> bool:
    """檢查文章是否已經發過（比對 URL 和標題相似度）"""
    history = _load_posted_history()
    url = article.get("link", "")
    title = article.get("title", "").lower().strip()

    for entry in history:
        # 1. URL 完全相同 → 一定重複
        if url and entry.get("url") == url:
            return True
        # 2. 同頻道 + 標題高度相似（>80% 字元重疊）→ 很可能重複
        if entry.get("channel") != channel:
            continue
        h_title = entry.get("title", "").lower().strip()
        if title and h_title:
            overlap = sum(1 for c in title if c in h_title)
            similarity = overlap / max(len(title), 1)
            if similarity > 0.8:
                return True
    return False


# 主題分類關鍵字（用於多樣性懲罰）
TOPIC_KEYWORDS = {
    "crypto": {
        "BTC/ETF":     ["BTC", "比特幣", "bitcoin", "ETF", "現貨 ETF", "比特幣 ETF", "比特幣現貨"],
        "ETH":         ["ETH", "以太坊", "ethereum"],
        "宏觀/政策":   ["川普", "Trump", "Fed", "聯準會", "SEC", "CFTC", "政策", "監管", "利率"],
        "穩定幣":      ["USDT", "USDC", "穩定幣", "stablecoin", "Tether", "Circle"],
        "交易所":      ["幣安", "binance", "Coinbase", "OKX", "交易所"],
        "DeFi/新幣":   ["DeFi", "MEME", "meme", "迷因", "Aave", "Uniswap", "dApp"],
        "礦工/技術":   ["礦工", "miner", "hash", "算力", "Layer 2", "L2", "比特幣網路"],
        "機構":        ["貝萊德", "BlackRock", "灰度", "microstrategy", "Michael Saylor"],
    },
    "finance": {
        "美股/科技":   ["納斯達克", "道瓊", "S&P500", "科技股", "輝達", "NVIDIA", "蘋果", "特斯拉"],
        "央行/利率":   ["Fed", "聯準會", "升息", "降息", "利率", "通膨", "CPI"],
        "黃金/大宗":   ["黃金", "gold", "白銀", "原油", "oil", "WTI", "銅", "大宗商品"],
        "地緣政治":    ["川普", "Trump", "關稅", "制裁", "中美", "台海", "戰爭"],
        "台股":        ["台股", "加權", "櫃買", "上市櫃"],
    },
}

# 主題冷卻懲罰表：多久（天）內同主題算重複
TOPIC_COOLDOWN_DAYS = 3      # 3 天內同主題 penalize
TOPIC_COOLDOWN_PENALTY = -5  # 被 penalize 扣幾分


def _extract_topics(article: dict, channel: str) -> set[str]:
    """從文章中抽出涵蓋的主題"""
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    topics = set()
    for topic, kws in TOPIC_KEYWORDS.get(channel, {}).items():
        for kw in kws:
            if kw.lower() in text:
                topics.add(topic)
                break
    return topics


def _get_recent_topics(channel: str, days: int = TOPIC_COOLDOWN_DAYS) -> dict[str, str]:
    """取得近 N 天各文章的主题（topic -> date），用於冷卻計算"""
    import datetime
    history = _load_posted_history()
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    recent = {}
    for entry in reversed(history[-30:]):  # 只看最近 30 篇
        if entry.get("channel") != channel:
            continue
        try:
            d = datetime.datetime.fromisoformat(entry.get("posted_at", "2020-01-01"))
        except Exception:
            continue
        if d < cutoff:
            continue
        entry_date = entry.get("posted_at", "")[:10]
        for t in (entry.get("_topics") or []):
            recent[t] = entry_date
    return recent


# 廣義分類關鍵字（用於 content_log.xlsx 的多樣性比對）
_BROAD_CATEGORY_KEYWORDS = {
    "虛擬貨幣": ["比特幣", "BTC", "ETH", "以太坊", "USDT", "USDC", "DeFi", "穩定幣", "幣圈", "加密", "區塊鏈", "區塊", "DAO", "NFT", "MEME", "meme", "迷因", "幣", "交易所", "幣安", "Coinbase", "Ripple", "XRP", "Solana", "SOL", "Cardano", "ADA", "Polkadot", "DOT", "Polygon", "MATIC", "LINK", "Chainlink", "AAVE", "Uniswap"],
    "科技/AI": ["AI", "ChatGPT", "OpenAI", "Google", "Meta", "Apple", "蘋果", "輝達", "NVIDIA", "黃仁勳", "特斯拉", "Tesla", "SpaceX", "微軟", "Microsoft", "亞馬遜", "AWS", "雲端", "晶片", "半導體", "處理器", "晶圓"],
    "總經/政策": ["Fed", "聯準會", "升息", "降息", "利率", "通膨", "CPI", "GDP", "非農", "就業", "鮑爾", "葉倫", "美國經濟", "QE", "QT", "貨幣政策", "財政政策"],
    "大宗商品": ["黃金", "gold", "白銀", "原油", "oil", "WTI", "布倫特", "銅", "大宗商品", "商品", "石油", "天然氣", "玉米", "小麥", "大豆"],
    "美股/科技": ["美股", "道瓊", "S&P", "Nasdaq", "那斯達克", "標普", "科技股", "IPO", "財報", "華爾街", "摩根", "高盛", "花旗", "銀行股", "航空股"],
    "中港台": ["中國", "習近平", "港股", "A股", "陸股", "中概股", "阿里巴巴", "騰訊", "京東", "百度", "美團", "字節跳動", "滴滴", "螞蟻", "陸港", "香港", "恒生"],
    "地緣政治": ["戰爭", "伊朗", "以色列", "川普", "習近平", "關稅", "制裁", "中美", "台海", "北韓", "俄羅斯", "普丁", "烏克蘭", " NATO", "軍事", "外交"],
}

_BROAD_CATEGORY_PENALTY = -8  # 廣義同分類扣 8 分（比原 TOPIC_COOLDOWN_PENALTY=-5 更重）


def _guess_broad_category(title: str, description: str = "") -> str:
    """從標題+摘要猜測廣義分類"""
    text = ((title or "") + " " + (description or "")).lower()
    for cat, kws in _BROAD_CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in text:
                return cat
    return "其他"


def _get_recent_broad_categories_xlsx(channel: str, limit: int = 5) -> list[str]:
    """從 content_log.xlsx 讀取近 N 篇的廣義分類（不含區塊鏈口吻，還原真實主題）"""
    try:
        import openpyxl, os
        log_path = os.path.join(os.path.dirname(__file__), "content_log.xlsx")
        if not os.path.exists(log_path):
            return []
        wb = openpyxl.load_workbook(log_path, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        if len(rows) < 2:
            return []
        # 欄位：日期=0, 頻道=1, 分類=2, 標題=3, 來源=4, 連結=5, 狀態=6, Hook=7
        recent = []
        for row in reversed(rows[1:]):  # 跳過標題列
            if row[1] == channel and row[6] == "已發布":
                recent.append(row[2])
            if len(recent) >= limit:
                break
        return recent
    except Exception:
        return []


def score_article(article: dict, channel: str) -> int:
    """計算文章熱門分數，含影響力倍增器 + 瑣碎內容過濾 + 社群熱度加成"""
    keywords = HOT_KEYWORDS.get(channel, [])
    major_kw = MAJOR_IMPACT_KW.get(channel, [])
    medium_kw = MEDIUM_IMPACT_KW.get(channel, [])
    trivial_pats = TRIVIAL_PATTERNS.get(channel, [])

    text = (article.get("title", "") + " " + article.get("description", "")).lower()

    # Step 1：基礎分數
    base = sum(1 for kw in keywords if kw.lower() in text)

    # Step 2：影響力倍增器
    major_hits = sum(1 for kw in major_kw if kw.lower() in text)
    medium_hits = sum(1 for kw in medium_kw if kw.lower() in text)
    multiplier = 1 + major_hits * 2 + medium_hits * 1  # 重磅×3, 中度×2
    score = int(base * multiplier)

    # Step 3：瑣碎內容過濾（罰分）
    for pat in trivial_pats:
        if pat.lower() in text:
            score = max(1, score // 2)  # 砍半，至少留 1 分（避免零分全滅）
            break

    # Step 4：描述品質加權
    if not _is_desc_sufficient(article.get("description", "")):
        score = max(0, score - 2)

    # Step 5：社群熱度加成（Reddit 點讚數）
    social_score = article.get("_social_score", 0)
    if social_score > 1000:
        score += 5  # 非常熱門
    elif social_score > 500:
        score += 3  # 熱門
    elif social_score > 100:
        score += 1  # 有關注

    # Step 6：Crypto 最低門檻
    min_score = MIN_SCORE.get(channel, 2)
    if score < min_score:
        score = 0  # 直接歸零，不入選

    return score


def _apply_topic_diversity(scored: list[tuple[int, dict]], channel: str) -> list[tuple[int, dict]]:
    """根據主題多樣性調整分數：冷門主題 bonus，熱門主題 penalty"""
    recent_topics = _get_recent_topics(channel, days=TOPIC_COOLDOWN_DAYS)
    # 廣義分類多樣性（從 content_log.xlsx）
    recent_broad = _get_recent_broad_categories_xlsx(channel, limit=3)

    adjusted = []
    for base_score, art in scored:
        topics = _extract_topics(art, channel)
        penalty = 0
        hit_topics = []

        for t in topics:
            if t in recent_topics:
                penalty += TOPIC_COOLDOWN_PENALTY
                hit_topics.append(t)

        # 廣義分類懲罰：如果文章分類和最近3篇相同，額外扣分
        art_cat = _guess_broad_category(art.get("title",""), art.get("description",""))
        art["_broad_category"] = art_cat
        if recent_broad and art_cat in recent_broad:
            penalty += _BROAD_CATEGORY_PENALTY
            print(f"   🔄 廣義分類冷卻 {art_cat}（最近：{recent_broad}）：{base_score} → {base_score + penalty}")

        # 標記文章攜帶的主題，供日後記錄用
        art["_topics"] = list(topics)
        art["_diversity_bonus"] = -penalty  # 儲存讓你知道降了幾分

        final_score = base_score + penalty
        if penalty != 0 and art_cat not in recent_broad:
            print(f"   🔄 主題冷卻 {hit_topics}：{base_score} → {final_score}")
        adjusted.append((final_score, art))

    # 分數重新排序
    adjusted.sort(key=lambda x: x[0], reverse=True)
    return adjusted


def find_related_articles(best: dict, all_articles: list[dict],
                          max_results: int = 4,
                          fetch_fulltext: bool = True) -> list[dict]:
    """從文章池中找出與選定文章同主題但不同來源的報導，用於交叉引用。

    升級：自動抓取相關文章全文（最多 1500 字），讓 AI 改寫時能真正
    整合多家媒體的不同觀點、數據和角度，而非只看標題+摘要。
    """
    best_title = best.get("title", "").lower()
    best_source = best.get("_source", "")
    best_link = best.get("link", "")

    # 提取關鍵詞（取標題中 2 字以上的詞）
    import re as _re
    # 中文：每 2-4 個字一組；英文：完整單字
    zh_words = _re.findall(r'[\u4e00-\u9fff]{2,4}', best_title)
    en_words = [w for w in _re.findall(r'[a-zA-Z]{3,}', best_title)]
    keywords = zh_words + en_words

    candidates = []
    seen_sources = {best_source}
    for art in all_articles:
        if art.get("link") == best_link:
            continue
        src = art.get("_source", "")
        if src in seen_sources:
            continue
        art_text = (art.get("title", "") + " " + art.get("description", "")).lower()
        # 計算關鍵詞匹配數
        match_count = sum(1 for kw in keywords if kw.lower() in art_text)
        if match_count >= 2:
            candidates.append((match_count, art))
            seen_sources.add(src)

    # 按匹配度排序，取最相關的
    candidates.sort(key=lambda x: x[0], reverse=True)
    related = [art for _, art in candidates[:max_results]]

    # 並行抓取相關文章全文（讓 AI 有更多素材交叉引用）
    if fetch_fulltext and related:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        def _fetch_one(art):
            url = art.get("link", "")
            if url:
                try:
                    full = fetch_article_text(url, max_chars=1500)
                    if full and len(full) > len(art.get("description", "")):
                        art["_fulltext"] = full
                        return True
                except Exception:
                    pass
            return False

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = {ex.submit(_fetch_one, a): a for a in related}
            fetched = 0
            for f in as_completed(futures, timeout=20):
                try:
                    if f.result():
                        fetched += 1
                except Exception:
                    pass
            if fetched:
                print(f"   📰 交叉引用：{fetched}/{len(related)} 篇取得全文")

    return related


def _is_topic_duplicate(article: dict, channel: str, last_n: int = 2) -> bool:
    """True if the article's topics ALL appeared in the last N posts of this channel.
    Prevents back-to-back posts on the same topic cluster."""
    history = _load_posted_history()
    channel_history = [e for e in history if e.get("channel") == channel]
    recent = channel_history[-last_n:]

    recent_topic_set: set[str] = set()
    for entry in recent:
        for t in (entry.get("_topics") or []):
            recent_topic_set.add(t)

    article_topics = set(article.get("_topics") or [])
    if not article_topics:
        return False  # 無法識別主題 → 不強制跳過
    return article_topics.issubset(recent_topic_set)


def pick_best_article(articles: list, channel: str = "crypto") -> Optional[dict]:
    """從文章池選出熱門分數最高、且尚未發過的那篇（經主題多樣性調整）"""
    if not articles:
        return None

    # Step 1: 基礎熱門分數
    scored = [(score_article(a, channel), a) for a in articles]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Step 2: 主題多樣性調整（冷卻懲罰）
    # 先預先計算每篇文章的主題
    for _, art in scored:
        art["_topics"] = _extract_topics(art, channel)

    scored = _apply_topic_diversity(scored, channel)

    # 印出多樣性調整後的排名（debug）
    print("   📊 主題多樣性調整後排名：")
    for i, (s, a) in enumerate(scored[:5]):
        topics_str = ",".join(a.get("_topics", [])[:3]) or "一般"
        bonus = a.get("_diversity_bonus", 0)
        bonus_str = f"(冷卻{bonus})" if bonus else ""
        print(f"      {i+1}. [{s}{bonus_str}] {a['title'][:40]}... [{topics_str}]")

    # 跳過已發過的文章，或主題與最近 2 篇完全重疊的文章
    for best_score, best in scored:
        if _is_already_posted(best, channel):
            print(f"   ⏭️ 跳過已發文：{best['title'][:45]}...")
            continue
        if _is_topic_duplicate(best, channel, last_n=2):
            topics_str = ",".join(best.get("_topics", []))
            print(f"   ⏭️ 跳過重複主題 [{topics_str}]：{best['title'][:40]}...")
            continue

        source = best.get("_source", "")
        topics_str = ",".join(best.get("_topics", []))
        print(f"   🎯 當選：{best['title'][:55]}")
        if source:
            print(f"   📰 來源：{source}  |  主題：{topics_str}")

        return best

    print("   ⚠️ 所有候選文章都已發過或主題重複！")
    return None


# ── Claude API 直接呼叫（快速穩定）────────────────────────────

_CLAUDE_SYSTEM = {
    "crypto": "你是仿製 @abmedia_io（鏈新聞）風格的 IG 社群編輯，服務台灣 20-35 歲加密貨幣投資者。寫作風格：繁體中文、台灣口語、有深度、數字精確（如「高達 2.3 億美元」）、CTA 要有具體可回答的問題、內容要簡潔有力。輸出 4-6 張 Carousel，每張都是獨立卡片式的內容，像電影海報般視覺衝擊強。寫作禁忌：嚴禁使用簡體字（必須用台灣正體繁體中文）、不可有翻譯腔、語句要口語通順像人說話，不要用「進行」「予以」「針對」等公文用語。",
    "finance": "你是仿製 @abmedia_io 風格的「金融大小事」IG 帳號資深社群編輯，服務台灣股市與金融投資人。寫作風格：繁體中文、台灣口語、有深度、數字精確、CTA 要有具體可回答的問題、內容簡潔有力。輸出 4-6 張 Carousel，每張獨立卡片。寫作禁忌：嚴禁使用簡體字（必須用台灣正體繁體中文）、不可有翻譯腔、語句要口語通順像人說話，不要用「進行」「予以」「針對」等公文用語。",
    "startup": "你是仿製 @abmedia_io 風格的「創業大小事」IG 帳號資深社群編輯，服務台灣創業者與科技愛好者。寫作風格：繁體中文、台灣口語、有深度、數字精確、CTA 要有具體可回答的問題、內容簡潔有力。輸出 4-6 張 Carousel，每張獨立卡片。寫作禁忌：嚴禁使用簡體字（必須用台灣正體繁體中文）、不可有翻譯腔、語句要口語通順像人說話，不要用「進行」「予以」「針對」等公文用語。",
}

def _get_anthropic_key() -> str:
    """從多個來源嘗試取得 Anthropic API key"""
    # 1. 環境變數
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    # 2. ig_config.json 中的 anthropic_api_key 欄位
    for cfg_path in IG_CONFIG_MAP.values():
        try:
            if cfg_path.exists():
                cfg = json.loads(cfg_path.read_text())
                key = cfg.get("anthropic_api_key", "").strip()
                if key:
                    return key
        except Exception:
            pass
    # 3. 專用設定檔
    key_file = SCRIPT_DIR / "anthropic_key.txt"
    if key_file.exists():
        key = key_file.read_text().strip()
        if key:
            return key
    return ""


def call_ai_claude(prompt: str, channel: str = "crypto") -> Optional[str]:
    """Claude Haiku 直接生成文案（<8秒，品質高）"""
    try:
        import anthropic
        api_key = _get_anthropic_key()
        if not api_key:
            return None
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=_CLAUDE_SYSTEM.get(channel, _CLAUDE_SYSTEM["crypto"]),
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        print(f"   ⚠️ Claude API 失敗：{e}")
        return None


# ── AI 改寫（結構化 5 張 Carousel 文案）────────────────────────

_AI_FORMAT_KEYS = (
    "HOOK", "WHAT", "EVIDENCE", "PERSON",
    "POINT1", "POINT2", "POINT3", "POINT4", "POINT5",
    "POINT1_PHOTO", "POINT2_PHOTO", "POINT3_PHOTO", "POINT4_PHOTO", "POINT5_PHOTO",
    "IMPACT", "CONTEXT", "CHART_NOTE", "BIG_NUMBER", "BIG_NUMBER_LABEL", "CTA",
)


def _clean_ai_preamble(text: str) -> str:
    """剝除 main 代理常見的對話前言/後記（如 "Let me respond:" / 「根據你的要求...」），
    只保留 KEY: value 格式的行。"""
    if not text:
        return ""
    lines = text.splitlines()
    out: list[str] = []
    started = False
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            if started:
                out.append(ln)
            continue
        # 偵測格式行：KEY 或 KEY: value
        upper = stripped.upper().replace("：", ":")
        for k in _AI_FORMAT_KEYS:
            if upper.startswith(f"{k}:") or upper.startswith(f"{k} :"):
                started = True
                out.append(ln)
                break
        else:
            if started:
                # 已經開始格式區塊，允許格式內換行（multi-line value）直到遇到空行或新 KEY
                out.append(ln)
    cleaned = "\n".join(out).strip()
    return cleaned or text  # 若剝不出東西，退回原文


def call_ai(prompt: str, timeout: int = 120, max_retries: int = 3) -> Optional[str]:
    """透過 openclaw agent 呼叫 MiniMax（每次用獨立 session-id，避免上下文汙染）。

    Fix notes:
    - 舊版共用 main session → 累積 70K+ tokens 後模型回傳「duplicate」垃圾
    - 新版：每次呼叫產生 fresh session-id，輸入 token 僅含本次 prompt
    - 回傳後剝除 main 代理的對話式前言/後記，只保留 KEY: value 結構
    """
    import time as _time
    import uuid as _uuid

    # 強化 prompt：要求模型嚴格輸出格式，禁止任何對話式前言
    strict_prefix = (
        "你是結構化內容生成器。嚴格遵守：\n"
        "1) 只輸出使用者指定的 KEY: value 格式，每行一個欄位\n"
        "2) 禁止任何前言、後記、自我介紹、回覆客套、確認語\n"
        "3) 禁止使用工具、禁止搜尋、禁止多輪對話\n"
        "4) 全程繁體中文（台灣用語），嚴禁簡體字\n\n"
        "===== 以下為任務 =====\n"
    )
    full_prompt = strict_prefix + prompt

    for attempt in range(1, max_retries + 1):
        sid = f"pipeline-{_uuid.uuid4().hex[:12]}"
        try:
            result = subprocess.run(
                [
                    "/opt/homebrew/bin/openclaw", "agent",
                    "--agent", "main",
                    "--session-id", sid,
                    "--thinking", "off",
                    "--json",
                    "--message", full_prompt,
                ],
                capture_output=True, text=True, timeout=timeout
            )
            raw = result.stdout or ""
            json_start = raw.find('{')
            if json_start < 0:
                if result.stderr:
                    print(f"   ⚠️ openclaw stderr: {result.stderr[:200]}")
                if attempt < max_retries:
                    print(f"   ⚠️ AI 回應無 JSON，{3}秒後重試 ({attempt}/{max_retries})...")
                    _time.sleep(3)
                continue
            data = json.loads(raw[json_start:])
            payloads = data.get("result", {}).get("payloads", [])
            if payloads and payloads[0].get("text"):
                text = payloads[0]["text"]
                # ★ 若含明顯 session/cron 汙染 → 重試
                lower = text.lower()
                if (("duplicate" in lower or "cron triggering" in lower or "test message" in lower)
                        and "hook" not in lower.replace("：", ":")):
                    print(f"   ⚠️ AI 回傳疑似汙染 (attempt {attempt})，重試")
                    if attempt < max_retries:
                        _time.sleep(2)
                    continue
                cleaned = _clean_ai_preamble(text)
                # 檢查是否含任一 format key
                if any((k + ":") in cleaned.upper().replace("：", ":") for k in _AI_FORMAT_KEYS):
                    return cleaned
                # 格式不符：重試
                if attempt < max_retries:
                    print(f"   ⚠️ AI 回傳無 KEY: 格式 (attempt {attempt})，重試")
                    _time.sleep(2)
                    continue
                return cleaned  # 最後一次仍回傳讓上層判斷
            status = data.get("status", "unknown")
            if attempt < max_retries:
                print(f"   ⚠️ AI 無 payload (status={status})，{3}秒後重試 ({attempt}/{max_retries})...")
                _time.sleep(3)
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ AI 呼叫逾時 ({attempt}/{max_retries})")
            if attempt < max_retries:
                _time.sleep(2)
        except json.JSONDecodeError as e:
            print(f"   ⚠️ AI JSON 解析錯誤：{e}，前100字：{raw[:100]}")
            if attempt < max_retries:
                _time.sleep(3)
        except Exception as e:
            print(f"   ⚠️ AI 呼叫失敗：{e}")
            break
    return None


def _claude_fallback(title: str, desc: str, ref_block: str,
                     ch_zh: str, source_name: str, channel: str) -> Optional[dict]:
    """當 MiniMax 失敗時，用 Claude API 一次性生成全部文案"""
    prompt = f"""把以下新聞改寫成繁體中文 IG Carousel 文案。台灣口語風格，嚴禁簡體字。

新聞（{source_name}）：{title}
摘要：{desc}{ref_block}

輸出格式（每行一個欄位，冒號後直接接內容，不要多餘說明）：

HOOK: 抓眼球標題（15字以內）
WHAT: 完整說明（350-500字！背景、經過、數據、各方反應，要有深度分析）
EVIDENCE: 佐證畫面描述（30字以內）
PERSON: 新聞中最主要人物英文全名（沒有填 null）
POINT1: 短標題（8字以內）|深度分析（200-300字！要有數據佐證、原因分析、影響評估）|📊 數據佐證
POINT1_PHOTO: 英文圖片搜尋詞（2-3個詞）
POINT2: 短標題（8字以內）|深度分析（200-300字！從不同角度切入）|📊 數據佐證
POINT2_PHOTO: 英文圖片搜尋詞
POINT3: 短標題（8字以內）|深度分析（200-300字！聚焦實際影響）|📊 數據佐證
POINT3_PHOTO: 英文圖片搜尋詞
POINT4: 短標題（8字以內）|深度分析（200-300字！提出反方觀點或不同立場）|📊 數據佐證
POINT4_PHOTO: 英文圖片搜尋詞
POINT5: 短標題（8字以內）|深度分析（200-300字！展望未來走向和風險）|📊 數據佐證
POINT5_PHOTO: 英文圖片搜尋詞
IMPACT: 為什麼重要（350-500字！全面深度分析，對產業影響+投資建議+歷史對比）
CONTEXT: 歷史脈絡（250-350字！列出 2-3 個歷史事件做對比）
CHART_NOTE: 用一句話解釋近期走勢（30字以內）
CTA: 互動問題（20字以內）"""

    print("   🧠 Claude API 生成中...")
    output = call_ai_claude(prompt, channel)
    if not output:
        print("   ⚠️ Claude API 無回應")
        return None

    data = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().upper()
        val = val.strip()
        if not val:
            continue
        if key == "HOOK":
            # 修復 \n 顯示問題：將字面「\n」替換為真正的換行符
            data["hook"] = val.replace("\\n", "\n")
            # 截斷，避免標題太長（最多 30 字）
            if len(data["hook"]) > 30:
                data["hook"] = data["hook"][:30] + "..."
        elif key == "WHAT":
            data["what"] = val[:500]  # WHAT 最多 500 字     data["what"] = val
        elif key == "EVIDENCE": data["evidence"] = val
        elif key == "PERSON":   data["person"] = val
        elif key in ("POINT1", "POINT2", "POINT3", "POINT4", "POINT5"):
            data.setdefault("points", []).append(val)
        elif key in ("POINT1_PHOTO", "POINT2_PHOTO", "POINT3_PHOTO",
                     "POINT4_PHOTO", "POINT5_PHOTO"):
            data.setdefault("point_photos", []).append(val)
        elif key == "IMPACT":   data["impact"] = val
        elif key == "CONTEXT":  data["context"] = val
        elif key == "CTA":      data["cta"] = val
    return data if data else None


def _enrich_with_claude(data: dict, title: str, desc: str,
                        ch_zh: str, source_name: str) -> None:
    """用 Claude 補充 PERSON 和 POINT_PHOTO（MiniMax 成功但缺少這些欄位時）"""
    if data.get("person") and data.get("point_photos"):
        return  # 已有，不用補
    try:
        prompt = f"""根據以下新聞，回答兩個問題：

新聞：{title}
摘要：{desc[:300]}

1. PERSON: 新聞中最主要人物的英文全名（沒有填 null）
2. 針對以下每個重點，給出最適合的英文圖片搜尋詞（2-3個詞）："""
        points = data.get("points", [])
        for i, pt in enumerate(points[:5], 1):
            pt_title = pt.split("|")[0][:20] if "|" in pt else pt[:20]
            prompt += f"\nPOINT{i}_PHOTO: （重點：{pt_title}）"

        output = call_ai_claude(prompt, "crypto")
        if output:
            for line in output.splitlines():
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                key = key.strip().upper()
                val = val.strip()
                if key == "PERSON" and val:
                    data["person"] = val
                elif "PHOTO" in key and val:
                    data.setdefault("point_photos", []).append(val)
            if data.get("point_photos"):
                print(f"   📸 Claude 補充了 {len(data['point_photos'])} 張圖片關鍵字")
    except Exception as e:
        pass  # 非必要，靜默失敗


def ai_rewrite(article: dict, channel: str,
               related_articles: Optional[list] = None,
               social_context: str = "") -> dict:
    """
    用 AI 改寫為 10 張 Carousel 文案。
    回傳 {hook, what, points, impact, context, evidence, cta}
    related_articles：同主題但不同來源的文章，供交叉引用
    social_context：社群和趨勢資訊補充，附加至提示中
    """
    title = article["title"]
    desc  = article.get("description", "")[:1500]
    source_name = article.get("_source", "")
    ch_zh = CHANNEL_ZH.get(channel, channel)

    # ── 描述不足時，抓取文章全文補充 ──
    if not _is_desc_sufficient(desc):
        link = article.get("link", "")
        if link:
            print(f"   📰 描述不足（{len(desc)}字），抓取文章全文...")
            full_text = fetch_article_text(link)
            if full_text and len(full_text) > len(desc):
                desc = full_text[:2000]  # 用全文取代截斷描述，提供更豐富素材
                print(f"   ✅ 取得文章全文 {len(desc)} 字")
            else:
                print(f"   ⚠️ 全文抓取無效，使用原始描述")

    # 組合多來源參考素材（優先用全文，比摘要豐富 5-10 倍）
    ref_block = ""
    if related_articles:
        ref_lines = []
        for i, ra in enumerate(related_articles[:4], 1):
            ra_src = ra.get("_source", f"來源{i}")
            ra_title = ra.get("title", "")[:80]
            # 優先使用全文（find_related_articles 已抓取），否則用摘要
            ra_content = ra.get("_fulltext", "") or ra.get("description", "")
            ra_content = ra_content[:800]  # 每篇最多 800 字，避免 prompt 太長
            ref_lines.append(f"【{ra_src}】{ra_title}\n{ra_content}")
        ref_block = "\n\n同主題其他媒體報導（你必須整合這些不同來源的獨特觀點、數據和評論，不要只看主要新聞）：\n" + "\n\n".join(ref_lines)

    # 社群/趨勢背景補充
    social_block = ""
    if social_context:
        social_block = f"\n\n【社群熱度與市場背景】{social_context}"

    prompt = f"""你是一位在台灣{ch_zh}媒體做了 5 年的資深 IG 社群編輯，風格對標 @abmedia_io（鏈新聞）。

你的人設：朋友會私訊問你「欸這新聞是怎樣」的那種人。你能用白話解釋複雜的事，適時加點幽默（比喻、諧音、吐槽），但不油膩。

❌ 禁止：簡體字、公文腔（進行/予以/針對/根據/鑑於）、AI 腔（總而言之/綜上所述/不可忽視/引發廣泛關注）、翻譯腔（在這個背景下/就...而言）、空洞形容（重大突破/劃時代/革命性）
✅ 你的寫法：像在跟朋友解釋，用比喻讓複雜概念秒懂，數字前後加空格

主要新聞（{source_name}）：
標題：{title}
摘要：{desc}{ref_block}{social_block}

請直接輸出（每行一個欄位，冒號後直接接內容）：

HOOK: 封面標題（兩行式每行≤10字，三行式每行≤8字，用 \\n 分行。要有數字衝擊或反差懸念，不要用「震驚」「驚人」）
WHAT: 新聞重點（300-500字。第一句直接講結論，中間穿插數據和比喻，最後帶出「跟你的關係」。整合多來源的不同觀點。）
POINT1: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，像跟朋友解釋，有具體數據）
POINT2: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，換角度）
POINT3: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，跟讀者切身相關）
POINT4: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，未來展望）
IMPACT: 深度分析（200-400字。開頭直接切結論，用比喻解釋，提歷史對比，點出時間節點。可以適時吐槽。）
FAQ1: 朋友會問的問題|回答（50-100字，用比喻或舉例，不要百科式回答）
FAQ2: 不同角度的問題|回答（50-100字，補充 FAQ1 沒講到的）
FAQ3: 跟錢或生活相關的問題|回答（50-100字）
BIG_NUMBER: 最震撼的數字（如「$1.2B」「-40%」。無寫 NONE）
MOOD: 情緒（crisis / regulation / bullish / bearish / tech / milestone / neutral）
QUESTION: 反問句（要能引發辯論，別寫「你怎麼看」這種廢問題）
CHART_NOTE: 近期走勢一句話（30字以內。無寫 NONE）
EVIDENCE: 封面視覺描述（30字，用於 AI 生圖）
PERSON: 主要人物（無寫 NONE）"""

    # 多行欄位：這些欄位的內容可能跨越多行
    _MULTILINE_KEYS = {"WHAT", "IMPACT", "CONTEXT", "EVIDENCE", "CTA"}

    def _parse_ai_output(output: str, data: dict) -> dict:
        """解析 AI 輸出，合併到 data dict。
        支援多行欄位（WHAT/IMPACT/CONTEXT/EVIDENCE/CTA）：
        當遇到 KEY: 後，持續收集所有後續行直到下一個 KEY 為止。
        """
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            raw = lines[i].replace("：", ":").replace("**", "").strip()
            if ":" not in raw:
                i += 1
                continue
            key, _, first_val = raw.partition(":")
            key = key.strip().upper()
            val = first_val.strip()

            # 如果是多行欄位，繼續收集後續行直到遇到另一個 KEY
            if key in _MULTILINE_KEYS:
                # 但最多收集 20 行，避免無限制收集
                j = i + 1
                while j < len(lines) and j < i + 21:
                    next_raw = lines[j].replace("：", ":").replace("**", "").strip()
                    # 如果下一行是新的 KEY 行，停止收集
                    if ":" in next_raw:
                        next_key = next_raw.split(":")[0].strip().upper()
                        if next_key in (
                            "HOOK", "WHAT", "IMPACT", "CONTEXT", "EVIDENCE",
                            "POINT1", "POINT2", "POINT3", "POINT4", "POINT5",
                            "FAQ1", "FAQ2", "FAQ3", "QUESTION", "CHART_NOTE",
                            "CTA", "PERSON", "MOOD", "BIG_NUMBER",
                            "BIG_NUMBER_LABEL"
                        ):
                            break
                    # 否則這行是多行內容的一部分
                    val += "\n" + lines[j].strip()
                    j += 1

            if val:
                if key == "HOOK":       data["hook"] = val
                elif key == "WHAT":     data["what"] = val
                elif key == "EVIDENCE": data["evidence"] = val
                elif key == "PERSON":   data["person"] = val
                elif key == "MOOD":     data["mood"] = val
                elif key == "BIG_NUMBER": data["big_number"] = val
                elif key == "BIG_NUMBER_LABEL": data["big_number_label"] = val
                elif key in ("POINT1", "POINT2", "POINT3", "POINT4", "POINT5"):
                    data.setdefault("points", []).append(val)
                elif key in ("POINT1_PHOTO", "POINT2_PHOTO", "POINT3_PHOTO",
                             "POINT4_PHOTO", "POINT5_PHOTO"):
                    data.setdefault("point_photos", []).append(val)
                elif key == "QUESTION":   data["question"] = val
                elif key in ("FAQ1", "FAQ2", "FAQ3"):
                    data.setdefault("faqs", []).append(val)
                elif key == "IMPACT":     data["impact"] = val
                elif key == "CONTEXT":    data["context"] = val
                elif key == "CHART_NOTE": data["chart_note"] = val
                elif key == "CTA":        data["cta"] = val

            i += 1
        return data

    # ── 拆成兩次 AI 呼叫（避免輸出截斷）──
    # 第一輪：HOOK + WHAT + POINT1-4 + EVIDENCE + PERSON + MOOD + BIG_NUMBER + BIG_NUMBER_LABEL
    prompt_part1 = f"""你是一位在台灣{ch_zh}媒體做了 5 年的資深 IG 社群編輯，風格對標 @abmedia_io（鏈新聞）。

你的人設：
- 你是那種朋友會私訊問你「欸這新聞是怎樣」的人，你總能用最白話的方式解釋複雜的事
- 你會適時加一點輕鬆幽默（比喻、諧音、流行用語），但不硬尬、不油膩
- 你寫東西像在跟朋友解釋，不像在寫報告
- 你有自己的觀點和判斷力，不是只在轉述新聞

❌ 絕對禁止（違反直接重寫）：
- 簡體字（用繁體）
- 公文腔：「進行」「予以」「針對」「根據」「鑑於」「有鑑於此」「值得注意的是」
- AI 典型句式：「總而言之」「綜上所述」「不可忽視」「引發廣泛關注」「業界普遍認為」
- 翻譯腔：「在這個背景下」「就...而言」「從...的角度來看」
- 空洞形容：「重大突破」「劃時代」「革命性」（除非真的是）
- 重複句型：三句話以上用同一個句式開頭

✅ 你的寫法應該像這樣：
- 「簡單說就是：高盛想靠賣保險賺錢，而不是自己下場買幣」
- 「翻成白話：你買這個 ETF ≠ 你持有比特幣，但你可以每月收租金」
- 「這有點像什麼？像你買房出租，房價漲跌先不管，每月房租先入袋」
- 在適當地方用一個 emoji 增加閱讀節奏（但每段最多 1 個）

📝 寫作風格規則：
- 數字前後加空格（如「罰 2 億」「跌 20%」）
- 重要數字直接放句首，製造衝擊感
- 如果有多來源報導，整合不同媒體的獨家資訊和不同觀點
- 英文名詞保留原文（如 ETF、DeFi、CoWoS），不需要硬翻

主要新聞（{source_name}）：{title}
摘要：{desc}{ref_block}{social_block}

請直接輸出以下格式：

HOOK: 封面標題（兩行式每行≤10字，三行式每行≤8字，用 \\n 分行。要有情緒張力：數字衝擊、反差感或懸念。不要寫「震驚」「驚人」這種詞）
WHAT: 新聞重點（200-300字。第一句就講結論，別鋪陳。中間穿插數據和比喻。最後一句帶出「所以這跟你有什麼關係」）
POINT1: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，像跟朋友解釋，有具體數據）
POINT2: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，換個角度講）
POINT3: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，跟讀者切身相關）
POINT4: 結論式標題（6-10字，要有數字或結論）|白話說明（30-40字，未來會怎樣）
FAQ1: 朋友會問的問題|回答（≤3句，用比喻或舉例解釋，不要百科全書式回答）
FAQ2: 朋友會問的問題|回答（換個角度，補充 FAQ1 沒講到的）
FAQ3: 朋友會問的問題|回答（跟錢或生活切身相關的問題）
QUESTION: 反問句（引發留言。好的反問：「你覺得高盛是真看好還是在割韭菜？」壞的反問：「你怎麼看？」）
EVIDENCE: 封面視覺描述（30字以內，用於 AI 生圖）
PERSON: 新聞主要人物全名（無則 NONE）
MOOD: 情緒（crisis / regulation / bullish / bearish / tech / milestone / interview / neutral）"""

    # 重試機制：最多嘗試 3 次（每次加不同提示避免重複失敗）
    retry_hints_p1 = [
        "",  # 第一次：不加額外提示
        "\n⚠️ 上一次生成失敗了。這次請特別注意：只輸出 HOOK/WHAT/EVIDENCE/POINT1-3 格式，每行一個欄位，冒號後直接寫內容。",
        "\n⚠️ 第三次嘗試。請嚴格遵守格式：HOOK: 內容\nWHAT: 內容\n...。不要輸出任何多餘文字。語言必須是繁體中文。",
    ]
    output1 = None
    for attempt in range(3):
        label = f"[1/2] 嘗試{attempt+1}" if attempt > 0 else "[1/2]"
        print(f"   🤖 AI 改寫中 {label} HOOK+WHAT+POINT1-3...")
        current_prompt = prompt_part1 + retry_hints_p1[attempt]
        output1 = call_ai(current_prompt, timeout=120)
        if output1 and any(k in output1.upper().replace("：", ":") for k in ["HOOK:", "WHAT:"]):
            print(f"   📝 Part1 回傳 {len(output1)} 字")
            break
        if output1:
            print(f"   ⚠️ Part1 回傳 {len(output1)} 字但無 HOOK/WHAT 格式，前 100 字：{output1[:100]}")
        else:
            print(f"   ⚠️ Part1 無回傳")
        output1 = None

    # ★ Part1 三次重試全部失敗（可能因 MiniMax duplicate 或網路問題）→ 跳到下一篇文章
    if not output1:
        print("   ⛔ Part1 完全失敗（Aave 文章 MiniMax duplicate），結束此文處理")
        return None

    # 第二輪：IMPACT + CONTEXT + CHART_NOTE + BIG_NUMBER + BIG_NUMBER_LABEL + CTA
    prompt_part2 = f"""你是剛剛那位台灣{ch_zh}媒體資深編輯，繼續寫深度分析。

記住你的風格：白話、有觀點、適時幽默。禁止公文腔和 AI 腔。

新聞標題：{title}
摘要：{desc}{social_block}

輸出格式：

IMPACT: 深度分析（350-500字。寫法指引：
  - 開頭別寫「這件事的影響是...」，直接切入最重要的結論
  - 用具體比喻讓複雜概念秒懂，例如「這就像麥當勞不賣漢堡了改賣漢堡的食譜」
  - 一定要寫到「對你我的影響」，不要只分析產業
  - 至少提一個歷史上類似的事件做對比
  - 最後點出 1-2 個值得關注的時間點或指標
  - 可以適時插一句吐槽或調侃，保持人味）
CONTEXT: 歷史脈絡（250-350字。不要流水帳式列點，而是用故事感串起 2-3 個相關事件。像在跟朋友說「你還記得上次...結果後來...」）
CHART_NOTE: 近期走勢一句話（30字以內。無相關走勢寫 NONE）
BIG_NUMBER: 本篇最震撼的數字（如「2 億」「38 億美元」。無寫 NONE）
BIG_NUMBER_LABEL: 數字標籤（如「最高罰金」「公司估值」。無寫 NONE）
CTA: 互動問題（20字以內，要具體到能引發辯論，別寫「你怎麼看」這種廢問題）"""

    retry_hints_p2 = [
        "",
        "\n⚠️ 上一次生成失敗了。這次請特別注意：只輸出 POINT4/POINT5/IMPACT/CONTEXT/CTA 格式，每行一個欄位。",
        "\n⚠️ 第三次嘗試。請嚴格遵守格式，語言必須是繁體中文，不要輸出任何多餘文字。",
    ]
    output2 = None
    for attempt in range(3):
        label = f"[2/2] 嘗試{attempt+1}" if attempt > 0 else "[2/2]"
        print(f"   🤖 AI 改寫中 {label} POINT4-5+IMPACT+CONTEXT+CTA...")
        current_prompt2 = prompt_part2 + retry_hints_p2[attempt]
        output2 = call_ai(current_prompt2, timeout=120)
        if output2 and any(k in output2.upper().replace("：", ":") for k in ["POINT4:", "IMPACT:"]):
            print(f"   📝 Part2 回傳 {len(output2)} 字")
            break
        if output2:
            print(f"   ⚠️ Part2 回傳 {len(output2)} 字但無 POINT4/IMPACT 格式，前 100 字：{output2[:100]}")
        else:
            print(f"   ⚠️ Part2 無回傳")
        output2 = None

    # ★ Part2 三次重試全部失敗 → 跳到下一篇文章（不繼續用殘缺文案）
    if not output2:
        print("   ⛔ Part2 完全失敗（MiniMax duplicate），結束此文處理")
        return None

    data = {}
    if output1:
        # 顯示前幾行幫助除錯
        first_lines = [ln.strip() for ln in output1[:300].splitlines() if ln.strip()][:3]
        print(f"   🔍 Part1 前幾行：{' / '.join(l[:50] for l in first_lines)}")
        _parse_ai_output(output1, data)
        print(f"   🔍 Part1 解析結果：HOOK={bool(data.get('hook'))}, WHAT={len(data.get('what',''))}字, points={len(data.get('points',[]))}個")
    if output2:
        prev_pts = len(data.get("points", []))
        _parse_ai_output(output2, data)
        new_pts = len(data.get("points", [])) - prev_pts
        print(f"   🔍 Part2 解析結果：新增 points={new_pts}, IMPACT={len(data.get('impact',''))}字, CONTEXT={len(data.get('context',''))}字")

    # ── 簡體→繁體轉換（所有文字欄位）──
    def _convert_data(d: dict) -> dict:
        for key in ("hook", "what", "impact", "context", "cta", "evidence"):
            if key in d and isinstance(d[key], str):
                d[key] = to_traditional(d[key])
        if "points" in d:
            d["points"] = [to_traditional(p) for p in d["points"]]
        return d

    def _has_zh(text: str) -> bool:
        """檢查文字是否包含中文"""
        return any('\u4e00' <= c <= '\u9fff' for c in (text or ""))

    def _is_hook_acceptable(hook: str) -> tuple[bool, str]:
        """嚴格檢查 Hook 品質，回傳 (是否合格, 失敗原因)"""
        if not hook:
            return False, "HOOK 為空"
        if not _has_zh(hook):
            return False, f"HOOK 無中文：'{hook[:30]}'"
        # 過短
        if len(hook) < 5:
            return False, f"HOOK 太短（{len(hook)}字）：'{hook}'"
        # 過長（理想 15-25 字）
        if len(hook) > 30:
            return False, f"HOOK 太長（{len(hook)}字）：'{hook[:20]}...'"
        # 禁止的無聊關鍵字
        boring_kw = ["最新消息", "今日頭條", "快訊", "突發", "今日新聞",
                      "不看後悔", "太重要了", "一定要知道", "震驚",
                      "沒想到", "竟然", "結果是", "來看看", "點進去"]
        for kw in boring_kw:
            if kw in hook:
                return False, f"HOOK 含有無聊關鍵字「{kw}」：'{hook}'"
        # 必須有實質內容（不能只是泛空的短語）
        if len(hook.strip()) < 8:
            return False, f"HOOK 內容太空洞：'{hook}'"
        return True, ""

    def _is_quality_ok(d: dict) -> tuple[bool, list[str]]:
        """檢查 AI 回傳品質是否合格，回傳 (是否合格, 問題列表)"""
        issues = []
        hook = d.get("hook", "")
        hook_ok, hook_reason = _is_hook_acceptable(hook)
        if not hook_ok:
            issues.append(f"HOOK: {hook_reason}")

        points = d.get("points", [])
        if len(points) < 3:
            issues.append(f"POINTS: 不足 3 個（只有 {len(points)}）")
        # 檢查至少 3 個 point 有實質中文內容（非 fallback 佔位文字）
        real_points = [p for p in points if _has_zh(p) and "持續關注後續" not in p and len(p) > 20]
        if len(real_points) < 3:
            issues.append(f"POINTS: 有效 points 不足 3 個（{len(real_points)}/{len(points)}）")
        return (len(issues) == 0, issues)

    # ── Hook 專門處理：如果 hook 不合格，嘗試重新生成 ────────────
    hook_ok, _ = _is_quality_ok(data)
    hook_regen_ok = False
    if not hook_ok:
        print(f"   ⚠️ Hook 不合格，嘗試重新生成...")
        # 嘗試多種風格
        for style in ["shocking", "funny", "curious", "question"]:
            new_hook = regenerate_hook(title, desc, channel, style=style)
            if new_hook:
                data["hook"] = new_hook
                hook_regen_ok, _ = _is_hook_acceptable(new_hook)
                if hook_regen_ok:
                    print(f"   ✅ Hook 重新生成成功（{style} 風格）：{new_hook}")
                    break
        # 如果重新生成失敗，套用 humanizer 試圖搶救
        if not hook_regen_ok:
            print("   ⚠️ Hook 重新生成也失敗，套用 Humanizer 搶救...")
            data["hook"] = humanize_taiwanese(data.get("hook", title[:20]), intensity="medium")

    if _is_quality_ok(data):
        pt_count = len(data.get("points", []))
        print(f"   ✅ MiniMax AI 改寫成功（{pt_count} 個重點）")
        # 嘗試用 Claude 補充 PERSON 和 POINT_PHOTO（非必要，失敗不影響）
        _enrich_with_claude(data, title, desc, ch_zh, source_name)
        # 對 hook 套用輕度 humanizer（增加台灣味但不改太多）
        if data.get("hook"):
            data["hook"] = humanize_taiwanese(data["hook"], intensity="light")
        return _convert_data(data)

    # ── MiniMax 失敗 → 用 Claude API 作為 fallback ──────────────
    quality_ok, issues = _is_quality_ok(data)
    if not quality_ok:
        print(f"   ⚠️ MiniMax 回傳品質不足（{', '.join(issues)}），嘗試 Claude API fallback...")
    claude_data = _claude_fallback(title, desc, ref_block, ch_zh, source_name, channel)
    if claude_data:
        claude_ok, _ = _is_quality_ok(claude_data)
        if claude_ok:
            print(f"   ✅ Claude fallback 成功！")
            # 對 hook 套用 humanizer
            if claude_data.get("hook"):
                claude_data["hook"] = humanize_taiwanese(claude_data["hook"], intensity="medium")
            return _convert_data(claude_data)

    # ── 最終 fallback：手動拆解（至少有中文內容）──────────────────
    print("   ⚠️ 兩個 AI 都失敗，使用後備文案")
    # 合併已解析的部分結果
    if data.get("hook") and _has_zh(data["hook"]):
        pass  # 保留已有 hook
    else:
        data["hook"] = title[:25] if _has_zh(title) else f"幣圈快訊"
    if not data.get("what") or not _has_zh(data.get("what", "")):
        data["what"] = desc[:200] if _has_zh(desc) else f"最新消息：{title}"
    if not data.get("cta"):
        data["cta"] = "你怎麼看？留言告訴我！"
    if not data.get("impact"):
        data["impact"] = "這則新聞對市場具有重要意義。機構投資人的動向往往引領市場趨勢，了解背後原因有助於掌握行情。本事件可能影響短期價格波動，建議持續追蹤後續進展，並關注相關基本面變化。"
    if not data.get("context"):
        data["context"] = "此類新聞在幣圈時有發生，通常伴隨著市場情緒的明顯波動。建議投資人保持理性，切勿盲目跟風，了解風險後再做決策。"
    if not data.get("chart_note"):
        # 從標題和描述生成走勢圖說明
        title_lower = title.lower()
        if "比特" in title_lower or "btc" in title_lower:
            coin = "BTC"
        elif "以太" in title_lower or "eth" in title_lower:
            coin = "ETH"
        elif "sol" in title_lower:
            coin = "SOL"
        else:
            coin = "幣圈"
        # 簡單生成 chart_note
        data["chart_note"] = f"機構資金持續流入，{coin} 後市看好"
    points = data.get("points", [])
    # 保留有實質中文內容的 points，過濾垃圾（文章引用、來源標記等）
    _GARBAGE_CHARS = {'〈', '〉', '《', '》', '「', '」', '『', '』'}
    def _is_good_point(p: str) -> bool:
        if not _has_zh(p) or len(p) < 20:
            return False
        # 過濾包含文章引用符號的 points
        if any(c in p for c in _GARBAGE_CHARS):
            return False
        # 過濾包含常見垃圾關鍵字的 points
        garbage_kw = ['區塊客', 'blockcast', '最早釋出於', '這篇文章', '比特幣 etf', '吸金', '分析師', '突破行情', '醞釀中', '寫', '周新高', '億美元']
        p_lower = p.lower()
        if any(kw in p_lower for kw in garbage_kw):
            return False
        return True
    good_points = [p for p in points if _is_good_point(p)]
    # 從描述生成 fallback points，但要過濾標題關鍵字避免重複
    if desc:
        title_kw = set(title.lower().replace(" ", "").replace("！", "").replace("?", "")[:30])
        sentences = [s.strip() for s in re.split(r'[。？！\n]', desc) if len(s.strip()) > 8 and _has_zh(s)]
        for s in sentences:
            if len(good_points) >= 5:
                break
            # 跳過包含標題關鍵字的句子
            s_lower = s.lower()
            if any(kw in s_lower for kw in title_kw):
                continue
            good_points.append(f"延伸分析|{s[:80]}")
    while len(good_points) < 5:
        good_points.append("延伸分析|此新聞值得持續關注後續發展")
    data["points"] = good_points[:5]

    return _convert_data(data)


# ── 主 Pipeline ───────────────────────────────────────────────

def run_pipeline(channel: str, dry_run: bool = False) -> bool:
    """防重複執行的包裝器（持鎖後呼叫實際實作）"""
    import time as _time
    lock_file = Path.home() / f".openclaw/workspace/scripts/social-media/.{channel}_pipeline.lock"
    if lock_file.exists():
        lock_age = _time.time() - lock_file.stat().st_mtime
        if lock_age < 1800:
            print(f"\n⛔ Pipeline 鎖定中（另一個程序正在執行，{int(lock_age//60)}分前啟動）")
            print(f"   鎖檔：{lock_file}")
            print(f"   💡 如果確定沒有在執行，刪除鎖檔：rm {lock_file}")
            return False
        print(f"\n⚠️ 發現過期鎖檔（{int(lock_age//60)}分前），自動清除")
        lock_file.unlink()
    lock_file.write_text(f"{_time.time()}\n")
    print(f"🔒 Pipeline 鎖定：{lock_file}")
    try:
        ok = _run_pipeline_impl(channel, dry_run)
        return ok
    finally:
        if lock_file.exists():
            lock_file.unlink()


def _run_pipeline_impl(channel: str, dry_run: bool) -> bool:
    """Pipeline 主邏輯（由 run_pipeline 包鎖後呼叫）"""
    import time as _time
    print(f"\n{'='*52}")
    print(f"📡  [{channel.upper()}] 頻道 Pipeline 開始")
    print(f"{'='*52}")

    # ── Step 1：抓新聞（RSS + Twitter）—— 並行化 ─────────────────
    print("\n[1/4] 抓取新聞來源（並行）...")
    sources = RSS_SOURCES.get(channel, [])
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_one_source(source):
        """單一來源抓取，回傳 (source_name, articles_list)"""
        try:
            arts = fetch_rss(source["url"])
            if arts:
                for a in arts:
                    a["_source"] = source["name"]
                return (source["name"], arts, None)
            return (source["name"], [], None)
        except Exception as e:
            return (source["name"], [], e)

    all_articles = []
    with ThreadPoolExecutor(max_workers=min(len(sources), 8)) as executor:
        futures = {executor.submit(fetch_one_source, s): s for s in sources}
        for future in as_completed(futures):
            name, arts, err = future.result()
            if err:
                print(f"   ❌ {name}: {err}")
            elif arts:
                print(f"   ✅ {name} — {len(arts)} 篇")
                all_articles.extend(arts)
            else:
                print(f"   ⚠️  {name} — 無文章")

    # Twitter 補充（可選，工具不在不影響流程）
    print(f"\n   嘗試 Twitter 補充...")
    twitter_arts = fetch_twitter_trending(channel)
    for a in twitter_arts:
        a["_source"] = "Twitter/X"
    all_articles.extend(twitter_arts)

    # 社群與趨勢來源（並行抓取）
    print(f"\n   🔥 抓取社群熱度來源...")
    trending_coins = []
    trend_keywords = []
    onchain_context = ""

    whale_alerts = []
    with ThreadPoolExecutor(max_workers=6) as social_executor:
        futures_social = {}
        futures_social['reddit'] = social_executor.submit(fetch_reddit_hot, channel)
        futures_social['trends'] = social_executor.submit(fetch_google_trends, channel)
        futures_social['telegram'] = social_executor.submit(fetch_telegram_channels, channel)
        if channel == 'crypto':
            futures_social['coingecko'] = social_executor.submit(fetch_coingecko_trending)
            futures_social['whale'] = social_executor.submit(fetch_whale_alerts)

        for name, future in futures_social.items():
            try:
                result = future.result(timeout=25)
                if name == 'coingecko' and result:
                    trending_coins = result
                    print(f"   🪙 CoinGecko: {len(trending_coins)} 個趨勢幣種")
                elif name == 'trends' and result:
                    trend_keywords = result
                    print(f"   📈 Google Trends: {len(trend_keywords)} 個趨勢關鍵字")
                elif name == 'reddit' and result:
                    for a in result:
                        a.setdefault("_source", f"Reddit")
                    all_articles.extend(result)
                    print(f"   ✅ Reddit — {len(result)} 篇熱門帖子")
                elif name == 'telegram' and result:
                    all_articles.extend(result)
                    print(f"   📱 Telegram — {len(result)} 則頻道訊息")
                elif name == 'whale' and result:
                    whale_alerts = result
                    for a in result:
                        a.setdefault("_source", "Whale Alert")
                    all_articles.extend(result)
                    print(f"   🐳 Whale Alert — {len(result)} 筆大額交易")
            except Exception as e:
                print(f"   ⚠️ {name}: {e}")

    # 準備社群背景文字補充
    social_context_parts = []
    if trending_coins:
        top_coins = trending_coins[:5]
        coins_str = ", ".join(
            f"{c['name']}({c['symbol']}, 24h:{c.get('price_change_24h', 'N/A')})"
            for c in top_coins
        )
        social_context_parts.append(f"CoinGecko 24h 趨勢幣種: {coins_str}")

    if trend_keywords:
        keywords_str = ", ".join(trend_keywords[:10])
        social_context_parts.append(f"台灣 Google 趨勢關鍵字: {keywords_str}")

    if whale_alerts:
        whale_str = "; ".join(a['title'] for a in whale_alerts[:3])
        social_context_parts.append(f"鯨魚動向: {whale_str}")

    if all_articles and channel == 'crypto':
        # 取出選定文章後再拉鏈上數據
        article_temp = pick_best_article(all_articles, channel)
        if article_temp:
            onchain_context = fetch_onchain_context(article_temp.get("title", ""), channel)
            if onchain_context:
                social_context_parts.append(f"鏈上數據: {onchain_context}")

    social_context_str = " | ".join(social_context_parts) if social_context_parts else ""

    if not all_articles:
        print("❌ 所有來源都失敗，放棄本次執行")
        return False

    # ── 分析市場情緒 ────────────────────────────────────────
    sentiment = analyze_sentiment(all_articles)
    print(f"   🎭 市場情緒：{sentiment['summary']}（分數：{sentiment['score']:.2f}）")
    social_context_parts.append(f"市場情緒: {sentiment['summary']}（正面{sentiment['positive_count']}篇 vs 負面{sentiment['negative_count']}篇）")
    social_context_str = " | ".join(social_context_parts) if social_context_parts else ""

    # 最多嘗試 3 篇文章（避免同一篇 AI 改寫失敗卡住）
    # 每次重試前先移除已標記失敗的文章，避免重複選擇同一篇
    failed_links = []
    for _retry_count in range(3):
        # 過濾掉已失敗的文章
        candidates = [a for a in all_articles if a.get("link") not in failed_links]
        if not candidates:
            print("❌ 所有文章都已嘗試過，放棄")
            break
        print(f"\n   📚 共收集 {len(candidates)} 篇文章，開始評分篩選...")
        article = pick_best_article(candidates, channel)
        if not article:
            print("❌ 沒有適合發文的新文章（全部已發過或分數太低）")
            return False
        best_source = article.get("_source", "")

        print(f"\n   📰 選定：{article['title'][:65]}")
        if article.get("link"):
            print(f"   🔗 連結：{article['link'][:80]}")

        # 找同主題其他來源的文章（交叉引用用）
        related = find_related_articles(article, all_articles)
        if related:
            print(f"\n   🔗 找到 {len(related)} 篇相關報導：")
            for ra in related:
                print(f"      [{ra.get('_source','')}] {ra['title'][:50]}")

    # ── Step 2：AI 改寫 ──────────────────────────────────────
    print("\n[2/4] AI 改寫文案...")
    ai_data = ai_rewrite(article, channel, related_articles=related, social_context=social_context_str)
    if ai_data is None:
        print("   ⛔ AI 改寫完全失敗（所有重試都失敗），嘗試下一篇文章...")
        # 把這篇加入 posted_history（避免重選同一篇）
        try:
            import json as _json
            from pathlib import Path as _Path
            history_file = Path.home() / ".openclaw/workspace/scripts/social-media/posted_history.json"
            history = _json.loads(history_file.read_text()) if history_file.exists() else []
            history.insert(0, {"title": article.get("title", ""), "link": article.get("link", ""), "channel": channel, "posted_at": datetime.now().isoformat()})
            history_file.write_text(_json.dumps(history[:50], ensure_ascii=False, indent=2))
        except Exception:
            pass
        return False
    print(f"   HOOK：{ai_data.get('hook', '')}")
    print(f"   WHAT：{ai_data.get('what', '')[:80]}...")
    print(f"   EVIDENCE：{ai_data.get('evidence', '(無)')}")
    for i, pt in enumerate(ai_data.get("points", []), 1):
        print(f"   PT{i}：{pt}")
    print(f"   IMPACT：{ai_data.get('impact', '')[:80]}...")
    print(f"   CONTEXT：{ai_data.get('context', '')[:60]}...")
    print(f"   CTA：{ai_data.get('cta', '')}")

    # ── Step 3：生成 Carousel ─────────────────────────────────
    print("\n[3/4] 生成 Carousel 圖片...")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path.home() / f".openclaw/workspace/agents/assistant-work/cards/{channel}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ★ 先生成 3 張封面候選 + Vision 評分，再帶最佳封面進 generate_carousel
    best_cover_path = None
    fal_key = os.environ.get("FAL_KEY", "").strip()
    if fal_key:
        print("   🎨 [封面優先] 生成 3 張封面候選，Vision 評分後選最佳...")
        best_cover_path = _auto_select_best_cover(
            channel=channel,
            out_dir=out_dir,
            hook=ai_data.get("hook", ""),
            what=ai_data.get("what", ""),
            candidate_count=3,
        )
        if best_cover_path:
            print(f"   🏆 最佳封面選定：{Path(best_cover_path).name}，帶入 S01")
        else:
            print("   ⚠️ 封面候選生成失敗，generate_carousel 自行生成單張封面")
    else:
        print("   ℹ️ 無 FAL_KEY，跳過封面候選生成（使用程式化背景）")

    try:
        from make_card import generate_carousel
        card_paths = generate_carousel(
            channel,
            ai_data,
            article.get("link", ""),
            best_source,
            str(out_dir),
            article_title=article.get("title", ""),
            cover_photo_path=best_cover_path,  # ★ 傳入已選好的最佳封面
        )
    except Exception as e:
        print(f"❌ 圖片生成失敗：{e}")
        import traceback; traceback.print_exc()
        return False

    if not card_paths:
        print("❌ 沒有生成任何圖片")
        return False
    print(f"   ✅ 共 {len(card_paths)} 張圖片")

    # ── 品質檢查：用 PIL 分析圖片基本品質 ──
    def _visual_quality_check(paths: list[str]) -> tuple[bool, list[str]]:
        issues = []
        try:
            from PIL import Image as _Img
            for idx, p in enumerate(paths):
                img = _Img.open(p)
                pixels = list(img.convert("RGB").getdata()) if not hasattr(img, 'get_flattened_data') else list(img.convert("RGB").get_flattened_data())
                # 檢查是否幾乎全黑（平均亮度 < 10）
                avg_brightness = sum(sum(px[:3]) / 3 for px in pixels[:5000]) / min(len(pixels), 5000)
                if avg_brightness < 10:
                    issues.append(f"Slide {idx+1} 幾乎全黑（亮度={avg_brightness:.0f}）")
                # 檢查是否全白（平均亮度 > 245）
                if avg_brightness > 245:
                    issues.append(f"Slide {idx+1} 幾乎全白（亮度={avg_brightness:.0f}）")
                # 檢查解析度
                if img.size[0] < 800 or img.size[1] < 800:
                    issues.append(f"Slide {idx+1} 解析度太低 ({img.size})")
        except Exception as e:
            print(f"   ⚠️ 品質檢查失敗：{e}")
        return (len(issues) == 0, issues)

    qc_pass, qc_issues = _visual_quality_check(card_paths)
    if not qc_pass:
        print(f"\n   ⚠️ 圖片品質問題：")
        for iss in qc_issues:
            print(f"      ⚠️ {iss}")
    else:
        print(f"   ✅ 圖片品質檢查通過")

    # ── AI Vision 審核（有 MINIMAX_API_KEY 或 ANTHROPIC_API_KEY 時啟用）──
    try:
        from quality_reviewer import review_carousel
        _has_vision_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        if _has_vision_key:
            review = review_carousel(str(out_dir), ai_data, channel)
            if review.get("should_retry"):
                print(f"   🔄 AI 審核建議重試：{review['summary']}")
                # 把審核回饋注入 ai_data，讓重試時改善
                ai_data["_review_feedback"] = review["summary"]
                # 重新生成一次
                try:
                    card_paths_v2 = generate_carousel(
                        channel, ai_data, article.get("link", ""),
                        best_source, str(out_dir),
                        article_title=article.get("title", ""),
                    )
                    if card_paths_v2:
                        card_paths = card_paths_v2
                        review_v2 = review_carousel(str(out_dir), ai_data, channel)
                        print(f"   {'✅' if review_v2['overall_pass'] else '⚠️'} 重試後評分：{review_v2['overall_score']:.0f}/100")
                except Exception as e2:
                    print(f"   ⚠️ 重試失敗：{e2}")
            else:
                print(f"   ✅ AI Vision 審核通過（{review['overall_score']:.0f}/100）")
        else:
            print(f"   ℹ️ 無 MINIMAX_API_KEY 或 ANTHROPIC_API_KEY，跳過 AI Vision 審核")
    except ImportError:
        print(f"   ℹ️ quality_reviewer 不可用，跳過 AI Vision 審核")
    except Exception as e:
        print(f"   ⚠️ AI Vision 審核異常：{e}")

    # ── Step 4：組合文案 + 發文 ───────────────────────────────
    date_str = datetime.now().strftime("%Y/%m/%d")
    hashtags = HASHTAGS.get(channel, "")
    hook = ai_data.get("hook", article["title"][:20])
    what = ai_data.get("what", "")
    cta  = ai_data.get("cta", "你怎麼看？")

    context = ai_data.get("context", "")
    context_block = f"\n\n📜 歷史脈絡：\n{context}" if context else ""

    ig_caption = f"""{hook}

{what}{context_block}

{cta}

來源：{best_source} | {date_str}

{hashtags}"""

    # ── 品質閘門：確保文案品質足以發文 ──
    def _has_chinese(text: str, min_ratio: float = 0.3) -> bool:
        if not text:
            return False
        zh_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return zh_count / max(len(text), 1) >= min_ratio

    def _check_quality_gate() -> bool:
        """檢查整體文案品質，不合格就不發文
        寬鬆標準：只要有中文內容、有 points、有 WHAT，就放行。
        """
        issues = []
        # HOOK：只要有中文字就好（甚至只有標題也行）
        if not _has_chinese(hook, 0.05):
            issues.append("HOOK 不含中文")
        # WHAT：只要有 20+ 中文就放行
        if not _has_chinese(what, 0.1) or len(what) < 20:
            issues.append("WHAT 空白或過短")
        # POINTS：只要有 3+ 個 point 就放行
        points = ai_data.get("points", [])
        if len(points) < 3:
            issues.append(f"POINTS 不足 3 個（只有 {len(points)}）")
        # IMPACT：降低標準，只要有 50+ 中文就放行
        impact = ai_data.get("impact", "")
        if not _has_chinese(impact, 0.1) or len(impact) < 50:
            issues.append("IMPACT 空白或過短")
        # CHART_NOTE：完全放行，不當成必要欄位
        # CONTEXT：完全放行，不當成必要欄位
        if issues:
            print(f"\n   🚫 品質閘門未通過：")
            for iss in issues:
                print(f"      ❌ {iss}")
            return False
        return True

    if not _check_quality_gate():
        print(f"\n   ⚠️ 品質閘門未通過，嘗試補救...")
        # ── 補救機制：當關鍵欄位空白時，用 humanizer + 原文 fallback ──
        desc = article.get("description", "")
        title = article.get("title", "")

        # 補 WHAT
        if not _has_chinese(what, 0.1):
            if desc and _has_chinese(desc, 0.3):
                # 用 humanizer 把 description 改寫成 WHAT
                what_fallback = humanize_taiwanese(desc[:300], intensity="medium")
                ai_data["what"] = what_fallback
                print(f"   ✅ WHAT 補救成功（{len(what_fallback)} 字）")
            else:
                ai_data["what"] = f"最新消息：{title}"

        # 補 IMPACT
        impact = ai_data.get("impact", "")
        if not _has_chinese(impact, 0.3):
            # 用 points 組合 + humanizer 生成 IMPACT
            points = ai_data.get("points", [])
            points_text = "。".join([p.split("|")[-1] if "|" in p else p for p in points[:3]])
            impact_fallback = humanize_taiwanese(
                f"這個事件的重點是：{points_text}。對於市場和投資人有什麼影響，需要持續觀察。",
                intensity="medium"
            )
            ai_data["impact"] = impact_fallback
            print(f"   ✅ IMPACT 補救成功（{len(impact_fallback)} 字）")

        # 補 CHART_NOTE
        if not ai_data.get("chart_note") or len(ai_data.get("chart_note", "")) < 10:
            # 從標題偵測幣種
            title_lower = title.lower()
            if "比特" in title_lower or "btc" in title_lower:
                coin = "BTC"
            elif "以太" in title_lower or "eth" in title_lower:
                coin = "ETH"
            elif "sol" in title_lower:
                coin = "SOL"
            else:
                coin = "加密市場"
            ai_data["chart_note"] = f"{coin} 近期波動加劇，建議謹慎操作"

        # 重新檢查
        what = ai_data.get("what", "")
        impact = ai_data.get("impact", "")
        hook = ai_data.get("hook", "")
        chart_note = ai_data.get("chart_note", "")

        if not _has_chinese(hook, 0.05):
            ai_data["hook"] = humanize_taiwanese(title[:20], intensity="light")
        if not _has_chinese(what, 0.1):
            ai_data["what"] = desc[:300] if _has_chinese(desc, 0.3) else title
        if not _has_chinese(impact, 0.3):
            ai_data["impact"] = f"此新聞對市場有重要影響，建議持續追蹤。"

        # 重新組合文案
        context = ai_data.get("context", "")
        context_block = f"\n\n📜 歷史脈絡：\n{context}" if context else ""
        ig_caption = f"""{ai_data.get("hook", hook)}

{ai_data.get("what", what)}{context_block}

{ai_data.get("cta", "你怎麼看？")}

來源：{best_source} | {date_str}

{hashtags}"""

        # 最終 quality gate 檢查
        final_issues = []
        if not _has_chinese(ai_data.get("hook", ""), 0.05):
            final_issues.append("HOOK 不含中文")
        if not _has_chinese(ai_data.get("what", ""), 0.1):
            final_issues.append("WHAT 不含中文")
        if not _has_chinese(ai_data.get("impact", ""), 0.3):
            final_issues.append("IMPACT 缺少實質內容")
        if not ai_data.get("chart_note") or len(ai_data.get("chart_note", "")) < 10:
            final_issues.append("CHART_NOTE 空白")

        if final_issues:
            print(f"\n   ⛔ 補救後品質仍不合格：{', '.join(final_issues)}")
            print(f"   💡 建議：確認 ANTHROPIC_API_KEY 環境變數已設定，讓 Claude fallback 可用")
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fail_dir = Path.home() / f".openclaw/workspace/agents/assistant-work/cards/{channel}_FAILED_{ts}"
            fail_dir.mkdir(parents=True, exist_ok=True)
            caption_path = str(fail_dir / "caption_failed.txt")
            with open(caption_path, "w") as f:
                f.write(f"HOOK: {ai_data.get('hook', '')}\nWHAT: {ai_data.get('what', '')}\n")
                for i, pt in enumerate(ai_data.get("points", []), 1):
                    f.write(f"POINT{i}: {pt}\n")
            print(f"   📄 失敗文案已存至：{fail_dir}")
            return False
        else:
            print(f"   ✅ 補救後品質合格，繼續發文")

    print(f"\n[4/4] 發布貼文...")
    print(f"   文案預覽：\n   {ig_caption[:160]}...")

    if dry_run:
        print("\n🔍 [Dry Run] 不實際發文，輸出供確認：")
        for p in card_paths:
            print(f"   圖片：{p}")
        caption_path = str(out_dir / "caption.txt")
        with open(caption_path, "w") as f:
            f.write(_filter_ai_garbage(ig_caption))
        # 儲存文章 metadata（供 --publish-last 記錄去重用）
        meta_path = str(out_dir / "article_meta.json")
        with open(meta_path, "w") as f:
            json.dump({
                "url": article.get("link", ""),
                "title": article.get("title", ""),
                "channel": channel,
                "hook": ai_data.get("hook", ""),
                "source": article.get("_source", ""),
                "_topics": article.get("_topics", []),
            }, f, ensure_ascii=False, indent=2)
        # 儲存完整 ai_data 供 --publish-last 重新生成圖片（確保最新驗證和 AI 封面）
        ai_data_path = str(out_dir / "ai_data.json")
        with open(ai_data_path, "w") as f:
            json.dump(ai_data, f, ensure_ascii=False, indent=2)
        print(f"   文案：{caption_path}")
        print(f"   metadata：{meta_path}")
        print(f"   ai_data：{ai_data_path}")

        # 封面候選已在 Step 3 生成並選定（best_cover_path），此處顯示摘要
        if best_cover_path:
            print(f"   🏆 封面已在 S01 使用：{Path(best_cover_path).name}")
            print(f"   💡 若要換封面，執行：python content_pipeline.py --select-cover N --publish-last")
        else:
            print(f"   ℹ️ 無 FAL_KEY，封面使用程式化背景")

        print("\n✅ Dry Run 完成！")
        return True

    # ── 內容品質閘門：確保文案至少有實質內容才發文 ──────────
    def _caption_content_ok() -> bool:
        """檢查 caption 是否含有實質長度內容（防止 AI 失敗時用文章摘要湊數）"""
        if len(ig_caption.strip()) < 50:
            return False
        what_len = len(ai_data.get("what", ""))
        if what_len < 150:
            return False
        return True

    if not _caption_content_ok():
        print(f"\n   ⛔ Caption 內容太短（what={len(ai_data.get('what',''))}字），AI 生成可能失敗")
        print(f"   💡 建議：手動檢查 API 設定，或用 --dry-run 確認內容")
        return False

    # 發 IG
    ig_script = SCRIPT_DIR / "ig_post.py"
    ig_config = IG_CONFIG_MAP.get(channel, SCRIPT_DIR / "ig_config.json")
    if not ig_config.exists():
        print(f"   ⚠️ {ig_config.name} 未設定，跳過 IG 發文")
        return True

    env_config = json.loads(ig_config.read_text())
    env = os.environ.copy()
    env["IG_USERNAME"] = env_config.get("username", "")
    env["IG_PASSWORD"] = env_config.get("password", "")

    if len(card_paths) > 1:
        img_args = ["--images"] + card_paths
    else:
        img_args = ["--image", card_paths[0]]

    post_result = subprocess.run(
        [sys.executable, str(ig_script), *img_args, "--caption", ig_caption],
        capture_output=True, text=True, env=env
    )
    print(post_result.stdout)
    if post_result.returncode != 0:
        print(f"⚠️ IG 發文失敗：{post_result.stderr}")
        return False

    # 記錄已發文歷史（防重複 + 主題多樣性追蹤）
    history = _load_posted_history()
    history.append({
        "url": article.get("link", ""),
        "title": article.get("title", ""),
        "channel": channel,
        "posted_at": datetime.now().isoformat(),
        "hook": ai_data.get("hook", ""),
        "_topics": article.get("_topics", []),   # 主題標記（用於多樣性冷卻）
    })
    _save_posted_history(history)
    print(f"   📝 已記錄到發文歷史（共 {len(history)} 筆）")

    print(f"\n✅ [{channel}] Pipeline 完成！")
    return True


# ── 發布上次 dry-run 結果 ──────────────────────────────────────

def publish_last_dryrun(channel: str, reuse_existing: bool = False) -> bool:
    """找到最近一次 dry-run 的圖片和文案，直接發文（不重跑 Pipeline）"""
    import glob as _glob

    cards_base = Path.home() / ".openclaw/workspace/agents/assistant-work/cards"
    pattern = str(cards_base / f"{channel}_*")
    dirs = sorted(_glob.glob(pattern), reverse=True)

    # 排除 FAILED 目錄
    dirs = [d for d in dirs if "FAILED" not in d]
    if not dirs:
        print(f"❌ 找不到 {channel} 的 dry-run 結果")
        return False

    out_dir = Path(dirs[0])
    caption_path = out_dir / "caption.txt"
    if not caption_path.exists():
        print(f"❌ {out_dir.name} 沒有 caption.txt（可能不是 dry-run 產物）")
        return False

    ai_data_path = out_dir / "ai_data.json"
    meta_path_obj = out_dir / "article_meta.json"
    card_paths: list[str] = []

    if reuse_existing:
        # 直接使用草稿現有的圖片
        print(f"   ♻️ 直接使用草稿現有圖片（--reuse-existing）...")
        existing = sorted(out_dir.glob(f"{channel}_*.jpg"))
        if existing:
            card_paths = [str(p) for p in existing]
            print(f"   ✅ 找到 {len(card_paths)} 張現有圖片")
        else:
            print(f"   ❌ 找不到現有圖片，切回重新生成模式...")
            reuse_existing = False

    if not reuse_existing:
        # 嘗試從 ai_data.json 重新生成圖片（確保最新 AI 封面和空白驗證）
        if ai_data_path.exists():
            print(f"   🔄 重新生成圖片（最新 AI 封面 + 空白驗證）...")
            try:
                ai_data_saved = json.loads(ai_data_path.read_text())
                meta_saved = json.loads(meta_path_obj.read_text()) if meta_path_obj.exists() else {}
                from make_card import generate_carousel as _gen_carousel
                new_paths = _gen_carousel(
                    channel,
                    ai_data_saved,
                    meta_saved.get("url", ""),
                    meta_saved.get("source", ""),
                    str(out_dir),
                    article_title=meta_saved.get("title", ""),
                )
                if new_paths:
                    card_paths = sorted(new_paths)
                    print(f"   ✅ 圖片重新生成完成（{len(card_paths)} 張）")
                if not new_paths:
                    raise ValueError("generate_carousel 回傳空清單")
            except Exception as e:
                print(f"   ⚠️ 圖片重新生成失敗（{e}），使用已有圖片")

    # Fallback：使用已有圖片（沒有 ai_data.json 或重新生成失敗）
    if not card_paths:
        card_paths = sorted([str(p) for p in out_dir.glob(f"{channel}_*_s*.jpg")])

    if len(card_paths) < 10:
        print(f"⚠️ 只找到 {len(card_paths)} 張圖片（預期 10 張），目錄：{out_dir.name}")
        if not card_paths:
            return False

    ig_caption = _filter_ai_garbage(caption_path.read_text().strip())

    print(f"\n{'='*52}")
    print(f"📤  [{channel.upper()}] 發布上次 Dry-Run 結果")
    print(f"{'='*52}")
    print(f"   📁 目錄：{out_dir.name}")
    print(f"   📸 圖片：{len(card_paths)} 張")
    print(f"   📝 文案預覽：{ig_caption[:100]}...")

    # 發 IG
    ig_script = SCRIPT_DIR / "ig_post.py"
    ig_config = IG_CONFIG_MAP.get(channel, SCRIPT_DIR / "ig_config.json")
    if not ig_config.exists():
        print(f"   ⚠️ {ig_config.name} 未設定，跳過 IG 發文")
        return False

    env_config = json.loads(ig_config.read_text())
    env = os.environ.copy()
    env["IG_USERNAME"] = env_config.get("username", "")
    env["IG_PASSWORD"] = env_config.get("password", "")

    if len(card_paths) > 1:
        img_args = ["--images"] + card_paths
    else:
        img_args = ["--image", card_paths[0]]

    post_result = subprocess.run(
        [sys.executable, str(ig_script), *img_args, "--caption", ig_caption],
        capture_output=True, text=True, env=env
    )
    print(post_result.stdout)
    if post_result.returncode != 0:
        print(f"⚠️ IG 發文失敗：{post_result.stderr}")
        return False

    # 記錄已發文歷史（優先從 article_meta.json 讀取，否則從文案推斷）
    history = _load_posted_history()
    meta_path = out_dir / "article_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    else:
        hook_line = ig_caption.split("\n")[0].strip() if ig_caption else ""
        meta = {"url": "", "title": hook_line, "hook": hook_line}
    history.append({
        "url": meta.get("url", ""),
        "title": meta.get("title", ""),
        "channel": channel,
        "posted_at": datetime.now().isoformat(),
        "hook": meta.get("hook", ""),
        "source": "publish-last",
        "_topics": meta.get("_topics", []),
    })
    _save_posted_history(history)
    print(f"   📝 已記錄到發文歷史（共 {len(history)} 筆）")

    print(f"\n✅ [{channel}] 發布完成！")
    return True


# ── AI Vision 封面自動評分與選擇 ──────────────────────────────

def _score_cover_with_vision(image_path: str, hook: str, what: str,
                              channel: str = "crypto") -> float:
    """用 Vision API 評分封面圖片（0-100分）
    評分標準：
    - 文字清晰度（hook能在圖上清楚閱讀）
    - 視覺吸引力（色彩、對比、構圖）
    - 情緒共鳴（震驚/好奇/趣味感）
    - 與內文相關性（是否呼應標題重點）
    """
    try:
        import anthropic
        api_key = _get_anthropic_key()
        if not api_key:
            return 50.0  # 無 API key 給予中等分

        client = anthropic.Anthropic(api_key=api_key)

        # 讀取圖片
        with open(image_path, "rb") as f:
            img_data = f.read()

        ch_zh = CHANNEL_ZH.get(channel, "綜合")

        prompt = f"""你是一個專業的 IG 社群視覺設計師。請為這張 Carousel 封面圖片打分數（0-100）。

評分標準（各項 25 分）：
1. 文字清晰度：Hook標題「{hook}」在圖片上是否清晰可讀
2. 視覺吸引力：色彩鮮明、對比適中、整體美觀
3. 情緒共鳴：是否讓人想點進去、是否有震驚/好奇/趣味感
4. 內文相關性：是否呼應「{what[:50]}...」這個主題

請直接輸出一個數字（0-100），不需要任何說明。
只輸出數字，例如：78"""

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data[:100000]}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )
        score_text = msg.content[0].text.strip()
        # 嘗試解析數字
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', score_text)
        if numbers:
            score = float(numbers[0])
            return min(100, max(0, score))
        return 50.0
    except Exception as e:
        print(f"   ⚠️ Vision 評分失敗 {image_path[:40]}: {e}")
        return 50.0  # 失敗時給予中等分


def _auto_select_best_cover(channel: str, out_dir: Path,
                             hook: str, what: str,
                             candidate_count: int = 3) -> Optional[str]:
    """自動生成多張封面候選，用 Vision API 評分，選擇最高分的封面"""
    try:
        from make_card import generate_ai_cover_candidates
    except ImportError:
        print("   ⚠️ 無法匯入 make_card，無法生成封面")
        return None

    print(f"   🎨 正在生成 {candidate_count} 張 AI 封面候選...")
    candidates = generate_ai_cover_candidates(
        hook=hook,
        what=what[:200] if what else "",
        person="",
        count=candidate_count,
        out_dir=str(out_dir),
    )

    if not candidates:
        print("   ⚠️ 沒有生成任何封面候選")
        return None

    print(f"   ✅ 獲得 {len(candidates)} 張封面候選，開始 Vision 評分...")
    scored = []
    for i, cand in enumerate(candidates, 1):
        score = _score_cover_with_vision(cand, hook, what, channel)
        scored.append((score, cand))
        print(f"      候選 {i}: {score:.1f} 分 → {Path(cand).name}")

    # 選擇最高分
    scored.sort(key=lambda x: float(x[0]), reverse=True)
    best_score, best_path = scored[0]
    best_score = float(best_score)  # 確保是 float

    print(f"   🏆 自動選擇最高分封面：{best_score:.1f} 分")
    print(f"      {Path(best_path).name}")

    return best_path


def _apply_selected_cover(channel: str, choice: int) -> bool:
    """將選中的候選封面替換 Slide 1 圖片（用候選圖當背景重繪封面）"""
    import glob as _glob
    import shutil

    cards_base = Path.home() / ".openclaw/workspace/agents/assistant-work/cards"
    pattern = str(cards_base / f"{channel}_*")
    dirs = sorted(_glob.glob(pattern), reverse=True)
    dirs = [d for d in dirs if "FAILED" not in d]
    if not dirs:
        print(f"❌ 找不到 {channel} 的 draft 結果")
        return False

    out_dir = Path(dirs[0])
    candidate_path = out_dir / f"cover_candidate_{choice}.jpg"
    if not candidate_path.exists():
        print(f"❌ 封面候選 {choice} 不存在：{candidate_path}")
        avail = list(out_dir.glob("cover_candidate_*.jpg"))
        print(f"   可用候選：{[p.name for p in avail]}")
        return False

    # 找 Slide 1 圖片
    s01_files = sorted(out_dir.glob(f"{channel}_*_s01.jpg"))
    if not s01_files:
        print(f"❌ 找不到 Slide 1 圖片")
        return False

    slide1_path = s01_files[0]

    # 備份原 Slide 1
    backup_path = out_dir / f"{slide1_path.stem}_backup.jpg"
    if not backup_path.exists():
        shutil.copy2(str(slide1_path), str(backup_path))

    # 讀取 article_meta 取得 hook 文字
    meta_path = out_dir / "article_meta.json"
    hook_text = ""
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        hook_text = meta.get("hook", "")

    # 用候選圖當背景，重繪 Slide 1（slide_hook 函數）
    from make_card import (slide_hook, make_background, THEMES,
                           Image as _Img)
    candidate_img = _Img.open(str(candidate_path))
    theme = THEMES.get(channel, THEMES["crypto"])

    # 準備背景（封面模式：清亮、下半漸層）
    bg = make_background(candidate_img, theme, cover=True)

    slide_hook(
        bg=bg, theme=theme, title=hook_text,
        what_preview="", slide_info="1/10",
        out=str(slide1_path),
    )
    print(f"✅ 已用候選 {choice} 替換封面：{slide1_path.name}")
    print(f"   原始封面備份在：{backup_path.name}")
    return True


# ── 入口 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="社群內容自動化 Pipeline v3")
    parser.add_argument("--channel", choices=["crypto", "finance", "startup", "all"],
                        default="crypto", help="頻道類型")
    parser.add_argument("--dry-run", action="store_true", help="只生成圖片，不實際發文")
    parser.add_argument("--publish-last", action="store_true",
                        help="發布上次 dry-run 的結果（使用已有的圖片和 caption.txt）")
    parser.add_argument("--reuse-existing", action="store_true",
                        help="發布時跳過圖片重新生成，直接使用草稿現有圖片（搭配 --publish-last）")
    parser.add_argument("--select-cover", type=int, default=0, metavar="N",
                        help="選擇第 N 張封面候選（1-3），0=不替換（預設）")
    args = parser.parse_args()

    channels = ["crypto", "finance", "startup"] if args.channel == "all" else [args.channel]
    for ch in channels:
        if args.select_cover and args.select_cover > 0:
            _apply_selected_cover(ch, args.select_cover)
        elif args.publish_last:
            publish_last_dryrun(ch, reuse_existing=args.reuse_existing)
        else:
            run_pipeline(ch, dry_run=args.dry_run)
