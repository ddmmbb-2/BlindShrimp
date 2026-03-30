import os
import json
import re
import sqlite3
from datetime import datetime
from openai import OpenAI

SKILL_NAME = 'SEARCH_ENGINE'
SKILL_DESC = "搜尋資料庫紀錄。支援日期轉換（如將『明天』轉為日期搜尋）與權重評分。"

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="sk-no-key-required")
MODEL_ALIAS = "gemma3:12b"
DB_PATH = os.path.join(os.getcwd(), "data", "records.db")

def extract_keywords(question):
    # 獲取當前時間以供 AI 計算相對日期
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    prompt = f"""你是一個搜尋專家。請將使用者的問題拆解成 2 到 8 個檢索關鍵字。
【目前系統時間】：{current_time}
規則：
1. 只能是短的名詞或動詞。
2. 絕對不可是句子。
3. 明天、後天、下週等詞彙「必須」根據目前時間換算成 YYYY-MM-DD 格式。

問題：{question}
輸出格式：{{"keywords": ["關鍵字1", "2026-03-25"]}}"""
    try:
        res = client.chat.completions.create(
            model=MODEL_ALIAS,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(res.choices[0].message.content).get("keywords", [])
    except:
        return [w for w in re.split(r'[ ,?？]', question) if len(w) > 1][:8]

def execute(action, **kwargs):
    if not os.path.exists(DB_PATH): return "尚未有紀錄。"
    keywords = extract_keywords(action)
    if not keywords: return "無法解析關鍵字。"

    scored_results = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, tags FROM records")
    rows = cursor.fetchall()
    
    for row in rows:
        rec_id, title, content, tags = row
        score = 0
        matched = []
        for kw in keywords:
            kw_l = kw.lower()
            hit = False
            if kw_l in (tags or "").lower(): score += 10; hit = True
            if kw_l in (title or "").lower(): score += 10; hit = True
            if kw_l in (content or "").lower(): score += 5; hit = True
            if hit: matched.append(kw)
        
        if score > 0:
            scored_results.append({"id": rec_id, "title": title, "content": content, "tags": tags, "score": score, "matched": list(set(matched))})
    
    conn.close()
    scored_results.sort(key=lambda x: x['score'], reverse=True)
    top_10 = scored_results[:10]

    if not top_10: return f"🔍 關鍵字 {keywords} 未命中結果。"

    output = f"🔍 搜尋結果（關鍵字：{', '.join(keywords)}）：\n"
    for i, res in enumerate(top_10, 1):
        output += f"{i}. 【{res['title']}】 (ID: {res['id']}) 分數:{res['score']}\n"
        output += f"   標籤: {res['tags']}\n   內容: {res['content'][:100]}...\n---\n"
    return output