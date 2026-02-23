#!/usr/bin/env python3
"""
真相網 - AI 新聞平台
功能：收集、整理並發布 AI / 科技新聞

使用方式：
python3 truth-network.py

功能模組：
1. 新聞爬蟲 - 從多個來源收集新聞
2. AI 摘要 - 使用 LLM 生成摘要
3. 分類標籤 - 自動分類
4. 發布系統 - 自動發布到網站/社群
"""

import requests
import json
from datetime import datetime

# ==== 配置 ====
NEWS_SOURCES = {
    "techcrunch": "https://techcrunch.com/feed/",
    "verge": "https://www.theverge.com/rss/index.xml",
    "wired": "https://www.wired.com/feed/rss",
    "mit_ai": "https://news.mit.edu/rss/topic/artificial-intelligence2",
}

# ==== 新聞來源列表（待擴充）====
SOURCES = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "科技"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "科技"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss", "category": "科技"},
    {"name": "MIT News AI", "url": "https://news.mit.edu/rss/topic/artificial-intelligence2", "category": "AI"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI"},
    {"name": "Google AI", "url": "https://blog.google/technology/ai/rss/", "category": "AI"},
]

# ==== RSS 爬蟲 ====
def fetch_rss_feed(source_url):
    """取得 RSS feed"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(source_url, headers=headers)
    return response.text

# ==== 新聞解析 ====
def parse_feed(xml_content, source_name):
    """解析 RSS XML"""
    import xml.etree.ElementTree as ET
    
    news_list = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for item in root.findall('.//item'):
            news = {
                'title': item.findtext('title', ''),
                'link': item.findtext('link', ''),
                'description': item.findtext('description', ''),
                'pubDate': item.findtext('pubDate', ''),
                'source': source_name,
                'collected_at': datetime.now().isoformat()
            }
            news_list.append(news)
            
    except Exception as e:
        print(f"❌ 解析錯誤：{e}")
        
    return news_list

# ==== AI 摘要（待整合 LLM）====
def generate_summary(news_item):
    """使用 LLM 生成摘要"""
    # TODO: 整合 MiniMax API
    title = news_item['title']
    
    # 暫時返回簡單描述
    summary = {
        'headline': title,
        'key_points': ['待使用 AI 生成'],
        'sentiment': '中性',
        'relevance_score': 0.5
    }
    
    return summary

# ==== 分類系統 ====
def categorize_news(news_item):
    """自動分類新聞"""
    title = news_item['title'].lower()
    
    categories = {
        'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt'],
        'Blockchain': ['bitcoin', 'crypto', 'blockchain', 'web3'],
        'Hardware': ['chip', 'processor', 'nvidia', 'apple', 'intel'],
        'Software': ['software', 'app', 'update', 'release'],
        'Policy': ['regulation', 'government', 'law', 'eu', 'china']
    }
    
    assigned = []
    for cat, keywords in categories.items():
        if any(kw in title for kw in keywords):
            assigned.append(cat)
    
    return assigned if assigned else ['一般']

# ==== 儲存到資料庫 ====
def save_to_database(news_list):
    """儲存到 JSON 資料庫"""
    db_file = 'news_database.json'
    
    # 讀取現有資料
    try:
        with open(db_file, 'r') as f:
            database = json.load(f)
    except:
        database = []
    
    # 加入新新聞
    database.extend(news_list)
    
    # 儲存
    with open(db_file, 'w') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"💾 已儲存 {len(news_list)} 篇新聞到資料庫")

# ==== 發布功能 ====
def publish_to_website(news_item):
    """發布到網站"""
    # TODO: 整合網站 API 或 static site generator
    print(f"🌐 發布：{news_item['title']}")
    pass

def publish_to_telegram(news_item):
    """發布到 Telegram"""
    # TODO: 整合 Telegram API
    print(f"📱 Telegram：{news_item['title']}")
    pass

# ==== 主程式 ====
def main():
    """主程式"""
    print("=== 真相網 - AI 新聞平台 ===")
    print(f"監控來源數量：{len(SOURCES)}")
    print("-" * 40)
    
    all_news = []
    
    for source in SOURCES:
        print(f"📰 抓取：{source['name']}...")
        
        try:
            xml = fetch_rss_feed(source['url'])
            news = parse_feed(xml, source['name'])
            all_news.extend(news)
            print(f"   ✅ 取得 {len(news)} 篇新聞")
        except Exception as e:
            print(f"   ❌ 錯誤：{e}")
    
    # AI 處理
    print("\n🤖 AI 處理中...")
    processed_news = []
    for news in all_news:
        summary = generate_summary(news)
        categories = categorize_news(news)
        
        news['summary'] = summary
        news['categories'] = categories
        processed_news.append(news)
    
    # 儲存
    print("\n💾 儲存到資料庫...")
    save_to_database(processed_news)
    
    # 發布
    print("\n🚀 發布...")
    for news in processed_news[:5]:  # 只發布前 5 篇
        publish_to_website(news)
    
    print("\n✅ 完成！")

if __name__ == "__main__":
    main()
