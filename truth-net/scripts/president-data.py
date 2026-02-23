#!/usr/bin/env python3
"""
總統資料整理腳本
真相網專用 - 整理歷任總統選前承諾 vs 實際政績

來源: 總統辯論會、政府公開資料、判決書、BBC等中立媒體
"""

import json
from datetime import datetime

def get_president_data():
    """總統資料結構"""

    presidents = {
        "蔡英文": {
            "term": "2016-2024 (兩屆)",
            "election": "2016, 2020",
            "promises": [],
            "achievements": [],
            "scandals": []
        },
        "賴清德": {
            "term": "2024-2028 (現任)",
            "election": "2024",
            "promises": [],
            "achievements": [],
            "scandals": []
        }
    }

    # 蔡英文 2016 選前承諾
    presidents["蔡英文"]["promises"] = [
        {
            "promise": "勞工政策 - 縮短年總工時",
            "source": "2016 辯論會",
            "status": "跳票",
            "progress": "0%",
            "details": "勞基法修惡，砍7天假"
        },
        {
            "promise": "居住正義 - 打房",
            "source": "2016 辯論會",
            "status": "跳票",
            "progress": "0%",
            "details": "房價所得比創歷史新高"
        },
        {
            "promise": "非核家園 - 2025再生能源20%",
            "source": "2016 政見",
            "status": "跳票",
            "progress": "15%",
            "details": "預計2025年綠能僅達15.2%"
        },
        {
            "promise": "司法改革",
            "source": "2016 政見",
            "status": "跳票",
            "progress": "10%",
            "details": "廢死跳票、吹哨者保護法未通過"
        },
        {
            "promise": "婚姻平權",
            "source": "2016 政見",
            "status": "部分完成",
            "progress": "50%",
            "details": "釋憲通過但立法延宕"
        },
        {
            "promise": "國會改革",
            "source": "2016 辯論會",
            "status": "跳票",
            "progress": "20%",
            "details": "不在籍投票未實現"
        },
        {
            "promise": "兩岸監督條例",
            "source": "2016 政見",
            "status": "跳票",
            "progress": "0%",
            "details": "草案仍在研議"
        },
        {
            "promise": "廢除監察院",
            "source": "2016 政見",
            "status": "跳票",
            "progress": "0%",
            "details": "反而提名酬庸監委"
        },
        {
            "promise": "軍公教年金改革",
            "source": "2016 政見",
            "status": "已完成",
            "progress": "100%",
            "details": "2018年完成"
        },
        {
            "promise": "長照2.0",
            "source": "2016 政見",
            "status": "部分完成",
            "progress": "55%",
            "details": "覆蓋率5成，但經費不足"
        }
    ]

    # 蔡英文實際政績
    presidents["蔡英文"]["achievements"] = [
        {
            "title": "同性婚姻合法化",
            "year": "2019",
            "category": "社會",
            "description": "亞洲第一個同性婚姻合法化國家"
        },
        {
            "title": "前瞻基礎建設",
            "year": "2017",
            "category": "建設",
            "description": "8800億預算",
            "controversy": "無具體有感建設"
        },
        {
            "title": "國艦國造",
            "year": "2016-2024",
            "category": "國防",
            "description": "4700億預算",
            "controversy": "進度延宕"
        },
        {
            "title": "離岸風電",
            "year": "2016-2024",
            "category": "能源",
            "description": "2兆預算",
            "controversy": "電價上漲疑慮"
        },
        {
            "title": "開放萊豬、核食",
            "year": "2016-2024",
            "category": "農業",
            "description": "開放日本核災區食品、萊豬進口",
            "controversy": "食安爭議"
        },
        {
            "title": "台美關係",
            "year": "2016-2024",
            "category": "外交",
            "description": "斷交13個邦交國",
            "controversy": "邦交國數量創新低"
        }
    ]

    # 蔡英文弊案/爭議
    presidents["蔡英文"]["scandals"] = [
        {
            "title": "論文門",
            "year": "2019-2023",
            "category": "學術詐欺",
            "description": "倫敦政經學院博士論文疑似造假",
            "source": "BBC, 路透社"
        },
        {
            "title": "私菸案",
            "year": "2019",
            "category": "貪污",
            "description": "特勤人員走私菸品1萬條",
            "amount": "免費"
        },
        {
            "title": "高端疫苗炒股",
            "year": "2021",
            "category": "內線交易",
            "description": "股價炒作疑雲",
            "source": "鏡週刊"
        },
        {
            "title": "萬里違建",
            "year": "2023",
            "category": "違建",
            "description": "老家違建爭議",
            "status": "未拆除"
        },
        {
            "title": "勞動基金虧損",
            "year": "2020-2023",
            "category": "財務管理",
            "description": "虧損5124.6億",
            "source": "審計部"
        },
        {
            "title": "舉債創新高",
            "year": "2016-2024",
            "category": "財政",
            "description": "8年舉債2.21兆",
            "source": "財政部"
        },
        {
            "title": "超思雞蛋",
            "year": "2023-2024",
            "category": "農業弊案",
            "description": "進口蛋爭議，浪費10億納稅錢",
            "source": "黃國昌質詢"
        }
    ]

    # 賴清德 2024 選前承諾 (2026年更新 - 已上任1年多)
    presidents["賴清德"]["promises"] = [
        {
            "promise": "產業轉型 - 半導體、AI、5+2產業",
            "source": "2024 辯論會",
            "status": "進行中",
            "progress": "40%",
            "details": "上任1年多，產業政策持續推動"
        },
        {
            "promise": "居住正義 - 社宅、囤房稅",
            "source": "2024 辯論會",
            "status": "進行中",
            "progress": "30%",
            "details": "社宅興建中，囤房稅修法待通過"
        },
        {
            "promise": "治安改善 - 槍擊案、詐騙",
            "source": "2024 辯論會",
            "status": "待加強",
            "progress": "20%",
            "details": "88槍案、imB詐騙案等"
        },
        {
            "promise": "打擊黑金槍毒詐",
            "source": "2024 政見",
            "status": "進行中",
            "progress": "25%",
            "details": "掃黑行動持續"
        },
        {
            "promise": "憲政改革 - 廢除考監",
            "source": "2024 政見",
            "status": "跳票",
            "progress": "0%",
            "details": "修憲門檻高，未有進展"
        },
        {
            "promise": "國防自主 - 潛艦國造",
            "source": "2024 政見",
            "status": "進行中",
            "progress": "35%",
            "details": "潛艦持續建造中"
        }
    ]

    # 賴清德實際政績 (2026年更新)
    presidents["賴清德"]["achievements"] = [
        {
            "title": "兵役延長",
            "year": "2024",
            "category": "國防",
            "description": "義務役恢復為1年"
        },
        {
            "title": "總預算增加",
            "year": "2024-2026",
            "category": "財政",
            "description": "中央政府總預算大幅增加",
            "controversy": "舉債爭議"
        },
        {
            "title": "對美關係",
            "year": "2024-2026",
            "category": "外交",
            "description": "過境美國、軍售加速"
        },
        {
            "title": "經濟成長",
            "year": "2025",
            "category": "經濟",
            "description": "GDP穩定成長",
            "controversy": "實質薪資停滯"
        }
    ]

    # 賴清德弊案/爭議 (2026年更新)
    presidents["賴清德"]["scandals"] = [
        {
            "title": "台南光電弊案",
            "year": "2024-2025",
            "category": "圖利",
            "description": "台南市中西區開發案、學甲爐渣案",
            "source": "黃國昌質詢"
        },
        {
            "title": "前助理共諜案",
            "year": "2024",
            "category": "國安",
            "description": "總統前助理涉入共諜案",
            "source": "BBC 報導"
        },
        {
            "title": "百億助理費案",
            "year": "2024-2025",
            "category": "貪污",
            "description": "台南市議會賄選案、助理費爭議",
            "status": "調查中/起訴"
        },
        {
            "title": "國會改革覆議案",
            "year": "2024",
            "category": "政治",
            "description": "藍白國會改革三法，民進黨覆議失敗",
            "status": "釋憲中"
        },
        {
            "title": "南電北送",
            "year": "2025",
            "category": "能源",
            "description": "北部供電爭議、停電問題",
            "status": "持續"
        }
    ]

    return presidents

def calculate_promise_completion(promises):
    """計算承諾完成率"""
    if not promises:
        return 0

    completed = sum(1 for p in promises if p.get("progress", "0%") == "100%")
    partial = sum(1 for p in promises if "0%" not in p.get("progress", "0%") and p.get("progress", "0%") != "100%")
    failed = sum(1 for p in promises if p.get("status") == "跳票")

    return {
        "completed": completed,
        "partial": partial,
        "failed": failed,
        "total": len(promises),
        "completion_rate": round((completed / len(promises)) * 100, 1)
    }

def generate_president_html(presidents):
    """生成 HTML 報告"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>總統政績對照 - 真相網</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }
        .president { margin: 30px 0; padding: 20px; background: #2d2d2d; border-radius: 8px; }
        .promise { padding: 10px; margin: 5px 0; background: #3d3d3d; border-radius: 4px; }
        .done { border-left: 4px solid #28a745; }
        .pending { border-left: 4px solid #ffc107; }
        .failed { border-left: 4px solid #dc3545; }
        h1 { color: #ff6b6b; }
        h2 { color: #feca57; }
        h3 { color: #54a0ff; }
        .progress { float: right; font-weight: bold; }
        .status-done { color: #28a745; }
        .status-pending { color: #ffc107; }
        .status-failed { color: #dc3545; }
        small { color: #aaa; }
        hr { border-color: #444; }
    </style>
</head>
<body>
    <h1>📊 總統政績對照 - 真相網</h1>
    <p>更新時間: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    <p>⚠️ 僅供個人研究用途 | 資料來源需交叉確認</p>
    <p>黃國昌 YouTube: <a href="https://www.youtube.com/@KC-Huang" style="color:#54a0ff;">https://www.youtube.com/@KC-Huang</a></p>
    <hr>
"""

    for name, data in presidents.items():
        completion = calculate_promise_completion(data.get("promises", []))

        html += f"""
    <div class="president">
        <h2>👤 {name}</h2>
        <p>任期: {data['term']} | 當選: {data['election']}</p>
        <p><strong>選前承諾完成率: {completion['completion_rate']}%</strong></p>
        <p>已完成: {completion['completed']} | 部分完成: {completion['partial']} | 跳票: {completion['failed']}</p>

        <h3>📋 選前承諾 vs 實際政績</h3>
"""

        for promise in data.get("promises", []):
            status_class = "done" if promise.get("progress") == "100%" else "pending" if promise.get("status") != "跳票" else "failed"
            status_text = f"<span class='status-{status_class}'>{promise.get('status', '未知')}</span>"

            html += f"""
        <div class="promise {status_class}">
            <span class="progress">{promise.get('progress', '0%')} {status_text}</span>
            <strong>{promise.get('promise', '未命名')}</strong><br>
            <small>來源: {promise.get('source', '未知')} | {promise.get('details', '')}</small>
        </div>
"""

        html += """
        <h3>🏆 實際政績</h3>
"""
        for achievement in data.get("achievements", []):
            html += f"""
        <div class="promise done">
            <strong>{achievement.get('title', '未命名')}</strong> ({achievement.get('year', '年份未知')})<br>
            <small>類別: {achievement.get('category', '未知')}</small><br>
            <small>{achievement.get('description', '')}</small>
        </div>
"""

        html += """
        <h3>⚠️ 弊案/爭議</h3>
"""
        for scandal in data.get("scandals", []):
            status = scandal.get('status', '調查中')
            html += f"""
        <div class="promise pending">
            <strong>{scandal.get('title', '未命名')}</strong> ({scandal.get('year', '年份未知')})<br>
            <small>類別: {scandal.get('category', '未知')} | 狀態: {status}</small><br>
            <small>{scandal.get('description', '')}</small>
        </div>
"""

        html += """
    </div>
"""

    html += """
    <hr>
    <p><small>⚠️ 資料僅供參考，請務必查證原始資料來源。</small></p>
</body>
</html>"""

    return html

def main():
    print("=" * 60)
    print("總統資料整理 - 真相網")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 取得資料
    presidents = get_president_data()

    # 印出摘要
    for name, data in presidents.items():
        completion = calculate_promise_completion(data.get("promises", []))
        print(f"\n👤 {name}")
        print(f"   任期: {data['term']}")
        print(f"   承諾完成率: {completion['completion_rate']}%")
        print(f"   跳票數: {completion['failed']}/{completion['total']}")

    # 生成 HTML
    html = generate_president_html(presidents)
    with open("president-report.html", 'w', encoding='utf-8') as f:
        f.write(html)

    # 儲存 JSON
    with open("president-data.json", 'w', encoding='utf-8') as f:
        json.dump(presidents, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已生成:")
    print(f"   📄 president-report.html (網頁報告)")
    print(f"   📊 president-data.json (原始資料)")

if __name__ == "__main__":
    main()
