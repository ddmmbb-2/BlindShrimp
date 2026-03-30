import threading
import time
import json
from datetime import datetime

SKILL_NAME = "SET_ALARM"
SKILL_DESC = "設定定時提醒。格式：'YYYY-MM-DD HH:mm:ss|提醒內容'。例如：'2026-03-29 20:50:00|開會'"

def background_reminder(target_time_str, task_content):
    """
    背景執行緒：等待時間到達，然後呼叫 LLM 產生提醒內容。
    """
    try:
        target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
        
        # 1. 持續檢查時間
        while datetime.now() < target_time:
            time.sleep(5) # 每 5 秒檢查一次
        
        # 2. 時間到了！從 app 載入必要的元件 (放在函數內避免循環引用)
        from app import client, MODEL_ALIAS, global_chat_history, write_memory, pending_notifications
        
        prompt = f"""
        【系統通知：時間已到】
        現在時間是：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        原定任務：{task_content}
        
        請你現在扮演 AI 助手，使用 CHAT 技能，以親切且幽默的語氣正式提醒使用者時間到了。
        請直接輸出 JSON 格式：
        {{
            "thought": "時間到了，我現在要提醒使用者...",
            "route": "CHAT",
            "action": "提醒文字內容"
        }}
        """
        
        # 3. 請求 LLM 生成提醒文字
        res = client.chat.completions.create(
            model=MODEL_ALIAS,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        result = json.loads(res.choices[0].message.content)
        ai_msg = result.get("action", f"嘿！時間到了，該做：{task_content} 囉！")
        
        # 4. 將訊息推送到全域提醒清單，讓前端輪詢抓取
        reminder_text = f"⏰ {ai_msg}"
        pending_notifications.append(reminder_text)
        
        # 5. 更新對話紀錄
        global_chat_history.append(f"AI (提醒): {reminder_text}")
        write_memory(f"System Trigger: {task_content} -> AI: {reminder_text}")
        
    except Exception as e:
        print(f"鬧鐘執行出錯: {e}")

def execute(action_input):
    try:
        # 分離時間與內容
        time_str, content = action_input.split('|')
        time_str = time_str.strip()
        content = content.strip()

        # 啟動背景執行緒 (只傳入兩個參數)
        thread = threading.Thread(
            target=background_reminder, 
            args=(time_str, content),
            daemon=True
        )
        thread.start()
        
        return f"好的，我已經定好鬧鐘了。會在 {time_str} 提醒你「{content}」。"
    except Exception as e:
        return f"設定失敗，請檢查格式是否為 'YYYY-MM-DD HH:mm:ss|內容'。錯誤：{e}"