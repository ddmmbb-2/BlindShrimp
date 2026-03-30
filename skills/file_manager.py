import os
import sqlite3
import json
from datetime import datetime
from openai import OpenAI

SKILL_NAME = 'DB_MANAGER'
SKILL_DESC = (
    "資料庫維護工具。指令：\n"
    "1. WRITE:內容 - 新增紀錄。\n"
    "2. DELETE:ID - 刪除指定 ID 的紀錄。\n"
    "3. READ:ID - 讀取完整內容。\n"
    "4. UPDATE:ID:新內容 - 修改現有紀錄，系統會重新生成標題與標籤。"
)

DB_PATH = os.path.join(os.getcwd(), "data", "records.db")
client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="sk-no-key-required")
MODEL_ALIAS = "gemma3:12b"

def ai_analyze(content):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # 將星期轉換為中文，能大幅降低 LLM 算錯日期的機率
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_str = weekdays[now.weekday()]

    # 強化 Prompt：加上星期幾，並明確要求把相對時間轉成絕對日期
    prompt = f"""【非常重要：目前系統基準時間為 {current_time} ({weekday_str})】
請根據此時間作為計算基準，分析以下內容。
注意：若內容包含「明天」、「後天」、「下週」等相對時間，請務必換算成正確的「絕對日期 (YYYY-MM-DD)」。
請輸出 JSON 格式 (title: 10字以內的簡短標題, tags: 包含換算後絕對日期的標籤字串，多個標籤請用逗號分隔)。
要分析的內容：{content}"""

    try:
        res = client.chat.completions.create(
            model=MODEL_ALIAS,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        
        # ==========================================
        # 防呆機制：確保 tags 和 title 絕對是字串
        # ==========================================
        if isinstance(data.get('tags'), list):
            data['tags'] = ", ".join(str(t) for t in data['tags'])
        else:
            data['tags'] = str(data.get('tags', ''))
            
        data['title'] = str(data.get('title', '未命名'))
        
        return data

    except Exception as e:
        print(f"AI 分析標籤時發生錯誤: {e}")
        return {"title": "未命名", "tags": ""}

def execute(action, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cmd = action.split(":", 1)[0].upper()
        
        # 刪除功能 (增加 rowcount 檢查)
        if cmd == "DELETE":
            # 這裡加入一個正則表達式或字串處理，確保只取數字
            raw_id = action.split(":")[1].strip()
            target_id = ''.join(filter(str.isdigit, raw_id)) # 強制只留數字
            
            if not target_id: return "錯誤：請提供正確的數字 ID。"
            
            cursor.execute("DELETE FROM records WHERE id = ?", (target_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return f"🗑️ 已成功刪除 ID 為 {target_id} 的紀錄。"
            else:
                return f"❌ 刪除失敗：資料庫中找不到 ID 為 {target_id} 的資料。"

        # 讀取詳細內容 (重寫前必用)
        elif cmd == "READ":
            target_id = action.split(":")[1].strip()
            cursor.execute("SELECT title, content, tags FROM records WHERE id = ?", (target_id,))
            row = cursor.fetchone()
            return f"📖 標題：{row[0]}\n標籤：{row[2]}\n內容：\n{row[1]}" if row else "找不到該 ID。"

        # 重寫/更新功能 (同樣增加 rowcount 檢查)
        elif cmd == "UPDATE":
            parts = action.split(":", 2)
            raw_id, new_content = parts[1].strip(), parts[2]
            target_id = ''.join(filter(str.isdigit, raw_id)) # 強制只留數字
            
            analysis = ai_analyze(new_content)
            cursor.execute(
                "UPDATE records SET title=?, content=?, tags=? WHERE id=?",
                (analysis['title'], new_content, analysis['tags'], target_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                return f"📝 ID {target_id} 已重寫成功！"
            else:
                return f"❌ 更新失敗：找不到 ID 為 {target_id} 的資料。"

        # 原有寫入功能
        elif cmd == "WRITE":
            raw_content = action.split(":", 1)[1]
            analysis = ai_analyze(raw_content)
            cursor.execute("INSERT INTO records (title, content, tags) VALUES (?, ?, ?)",
                           (analysis['title'], raw_content, analysis['tags']))
            conn.commit()
            return f"✅ 已存入！標題：{analysis['title']}"
            
        return "指令格式錯誤。"
    except Exception as e: return f"錯誤: {e}"
    finally: conn.close()