import os
import sys
import time
import json
import importlib.util
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# ==========================================
# 系統與 API 設定 (回歸標準 Flask 設定)
# ==========================================
app = Flask(__name__)

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="sk-no-key-required")
MODEL_ALIAS = "gemma3:12b"
MEMORY_FILE = "memory.txt"
SKILLS_DIR = "skills"

global_chat_history = []
pending_notifications = []

# ==========================================
# 基礎設施 (保持不變)
# ==========================================
def load_skills():
    skills = {}
    if not os.path.exists(SKILLS_DIR): return skills
    for filename in os.listdir(SKILLS_DIR):
        if filename.endswith(".py"):
            name = filename[:-3]
            path = os.path.join(SKILLS_DIR, filename)
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[name] = mod
                spec.loader.exec_module(mod)
                if hasattr(mod, "SKILL_NAME") and hasattr(mod, "execute"):
                    skills[mod.SKILL_NAME] = {"desc": mod.SKILL_DESC, "execute": mod.execute}
            except Exception: pass
    return skills

def read_memory():
    if not os.path.exists(MEMORY_FILE): return "尚無歷史記憶。"
    with open(MEMORY_FILE, "r", encoding="utf-8") as f: return f.read().strip()

def write_memory(content):
    if not content or not content.strip(): return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = f"[{now}] {content}\n"
    old_memory = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f: old_memory = f.read()
    updated_memory = (old_memory + new_entry)[-2000:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f: f.write(updated_memory)

# ==========================================
# 步驟 2：決策腦 (Planner) - 強化整理指令
# ==========================================
def decide_skill(user_input, current_memory, chat_history, step_history, available_skills, image_data=None):
    skills_info = "\n".join([f'- "{k}": {v["desc"]}' for k, v in available_skills.items()])
    routes = " 或 ".join([f'"{k}"' for k in available_skills.keys()])
    now = datetime.now()
    history_str = "\n".join(chat_history) if chat_history else "尚無對話紀錄。"

    prompt = f"""你是一個具備邏輯推理與資料整合能力的專業執行員。
【目前系統時間】：{now.strftime("%Y-%m-%d %H:%M:%S")}
【歷史記憶】：{current_memory}
【本次任務】：{user_input}
【執行進度】：{step_history if step_history else '尚未開始'}
【可用技能】：{skills_info}

【行為指令】：
1. **資料消化**：如果【執行進度】中已有網頁內容，你必須整理其內容，禁止只回覆「已完成」。
2. **終結路由**：當你準備好要回覆給使用者最終答案時，請務必選擇 "CHAT" 路由。
3. **整理要求**：在 CHAT 的 action 中，請提供條理清晰、重點明確的摘要。

請輸出 JSON：
{{
  "thought": "我已經讀取了內容，現在我將進行整理並透過 CHAT 回覆使用者...",
  "route": {routes},
  "action": "指令內容"
}}"""

    messages_content = [{"type": "text", "text": prompt}]
    if image_data: messages_content.append({"type": "image_url", "image_url": {"url": image_data}})

    try:
        res = client.chat.completions.create(
            model=MODEL_ALIAS,
            messages=[{"role": "user", "content": messages_content}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        return {"route": "CHAT", "action": f"決策錯誤: {e}"}







# ==========================================
# 網頁路由與 API 處理
# ==========================================
@app.route("/api/poll", methods=["GET"])
def poll():
    global pending_notifications
    if pending_notifications:
        # 取出第一條訊息發送給前端
        msg = pending_notifications.pop(0)
        return jsonify({"new_message": msg})
    return jsonify({"new_message": None})






@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    global global_chat_history
    data = request.json
    user_input = data.get("message", "")
    image_data = data.get("image")

    if not user_input.strip() and not image_data:
        return jsonify({"response": "請輸入有效訊息或提供圖片。"})

    log_user_input = user_input + (" [使用者傳送了一張圖片]" if image_data else "")
    global_chat_history.append(f"User: {log_user_input}")
    
    step_counter = 1
    step_history = ""
    available_skills = load_skills()
    
    while True:
        current_memory = read_memory()
        decision = decide_skill(user_input, current_memory, global_chat_history, step_history, available_skills, image_data)
        
        route = decision.get("route", "CHAT")
        action = decision.get("action", "")
        
        # 執行技能
        skill_info = available_skills.get(route)
        observation = skill_info["execute"](action) if skill_info else "找不到技能"
        
        # --- 【關鍵修改：快速通道】 ---
        # 如果大腦決定用 CHAT，直接回傳給前端，略過總結腦
        if route == "CHAT":
            ai_response = action if action else observation
            global_chat_history.append(f"AI: {ai_response}")
            write_memory(f"User: {log_user_input}\nAI: {ai_response}")
            return jsonify({"response": ai_response})
        
        # 如果是 READ_PAGE，記錄結果，準備進行下一輪整理
        step_history += f"\n[步 {step_counter}] 使用 {route}。結果: {observation}"
        step_counter += 1
        
        if step_counter > 10:
             return jsonify({"response": "執行過久，已中斷。"})
        time.sleep(0.5)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)