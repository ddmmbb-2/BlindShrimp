
# 🦐 BlindShrimp (瞎忙蝦)

> *"It looks like it's blindly looping, but it actually knows what it's doing."*
> *"看似在迴圈裡瞎忙，其實大腦算得比誰都精。"*

**BlindShrimp** is an extremely lightweight, Flask-based AI Agent framework. Say goodbye to heavy wrappers like LangChain, and return to pure Python logic. It features a built-in decision engine (Planner), dynamic skill loading, persistent memory, and multimodal vision.
**BlindShrimp (瞎忙蝦)** 是一個極度輕量、基於標準 Flask 打造的 AI Agent 框架。告別肥重的 LangChain，回歸最純粹的 Python 邏輯。只要單一檔案就能跑起具備決策大腦、動態技能加載、長期記憶與圖片辨識的本地端代理。

---

## ✨ Features | 核心特色

* 🧠 **Dynamic Planner (動態決策腦)**
  The core `decide_skill` engine automatically analyzes the task, memory, and current progress to decide whether to call external skills or reply directly.
  核心的 `decide_skill` 引擎會自動判斷目前進度，決定要呼叫外部技能，還是直接回答使用者。

* 🛠️ **Hot-pluggable Skills (熱插拔技能包)**
  Simply drop a Python script into the `skills/` directory, and the system will load it dynamically. Expanding capabilities is as easy as peeling a shrimp!
  將 Python 腳本丟進 `skills/` 資料夾，系統會自動動態載入。擴充功能就像剝蝦殼一樣簡單！

* 👁️ **Multimodal Vision (視覺多模態)**
  This shrimp has eyes! It supports `image_data` input, combining visual understanding with context for better reasoning.
  這隻蝦有眼睛！支援圖片傳入，能結合視覺與上下文進行推理。

* ⚡ **Fast Track Routing (快速通道)**
  When the brain decides to just "CHAT", it bypasses unnecessary loops and delivers the answer to the frontend instantly. No dragging, no wasting time.
  當大腦決定只需使用 `CHAT` 路由時，會直接略過冗長的總結步驟，瞬間把答案送到前端，絕不拖泥帶水。

* 📝 **Persistent Memory (長期記憶)**
  Automatically maintains `memory.txt` to keep track of the conversation context. It won't get amnesia halfway through the chat.
  自動維護 `memory.txt`，確保 Agent 記住過去的對話脈絡，不會聊到一半失憶。

---

## 🚀 Quick Start | 快速開始

### Prerequisites | 系統要求
* Python 3.8+
* [Ollama](https://ollama.com/) running locally (Default uses `gemma3:12b` via the OpenAI-compatible endpoint).
* 本地端需運行 Ollama（預設透過 OpenAI 相容 API 呼叫 `gemma3:12b` 模型）。

### Installation | 安裝步驟

**1. Clone the repository (複製專案)**
```bash
git clone [https://github.com/your-username/BlindShrimp.git](https://github.com/your-username/BlindShrimp.git)
cd BlindShrimp
```

**2. Install dependencies (安裝套件)**
```bash
pip install flask openai
```

**3. Run the agent (啟動瞎忙蝦)**
Ensure your Ollama is running, then start the Flask server:
確保你的 Ollama 已經啟動，接著執行 Flask 伺服器：
```bash
python app.py
```
Open your browser and visit (打開瀏覽器並前往): `http://localhost:5000`

---

## 📂 Project Structure | 專案架構

```text
BlindShrimp/
├── app.py               # The Core Brain & Server (核心大腦與伺服器)
├── memory.txt           # Persistent conversation memory (自動生成的長期記憶)
├── templates/
│   └── index.html       # Chat interface (前端對話介面)
└── skills/              # Put your skill scripts here (自定義技能資料夾)
    ├── search_web.py    # Example skill (技能範例)
    └── ...
```

---

## 🛠️ How to Add a Skill | 如何新增技能

Create a new `.py` file in the `skills/` folder. The framework requires two specific variables and one function:
在 `skills/` 資料夾中建立一個新的 `.py` 檔案。框架會自動抓取以下變數與函式：

```python
# skills/my_skill.py

SKILL_NAME = "MY_NEW_SKILL"
SKILL_DESC = "Use this skill to do something awesome. (提供給 LLM 判斷用的技能描述)"

def execute(action_input):
    # Your custom logic here
    # 你的自定義執行邏輯
    return f"Successfully executed with input: {action_input}"
```

---

## 📜 License | 授權條款

MIT License. See `LICENSE` for more information.
本專案採用 MIT 授權條款。
```
