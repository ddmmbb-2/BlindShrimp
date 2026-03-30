import os
import platform
import subprocess
import webbrowser

SKILL_NAME = 'OPEN_APP'
SKILL_DESC = '幫助使用者開啟電腦內的應用程式(如記事本、小算盤)或常見知名網站(如臉書、巴哈姆特、Netflix)。Action 請填寫「軟體名稱」或「網站名稱」。'

def execute(action, **kwargs):
    if not action:
        return "錯誤：請提供要開啟的應用程式或網站名稱。"

    action = action.strip().lower()
    system_os = platform.system()

    # ==========================================
    # 1. 常用網站對照表 (可自行擴充)
    # ==========================================
    websites = {
        "臉書": "https://www.facebook.com",
        "facebook": "https://www.facebook.com",
        "巴哈姆特": "https://www.gamer.com.tw",
        "巴哈": "https://www.gamer.com.tw",
        "netflix": "https://www.netflix.com",
        "網飛": "https://www.netflix.com",
        "github": "https://github.com",
        "推特": "https://twitter.com",
        "x": "https://twitter.com"
    }

    # 如果是網站，直接用預設瀏覽器打開
    for name, url in websites.items():
        if name in action:
            webbrowser.open(url)
            return f"🌐 已為您開啟網站：{name}"

    # ==========================================
    # 2. 本地應用程式對照表 (以 Windows 為主)
    # ==========================================
    apps_windows = {
        "記事本": "notepad.exe",
        "小算盤": "calc.exe",
        "計算機": "calc.exe",
        "終端機": "cmd.exe",
        "小畫家": "mspaint.exe",
        "檔案總管": "explorer.exe",
        "設定": "ms-settings:"
    }

    try:
        if system_os == "Windows":
            # 尋找是否符合常用的 Windows 軟體
            for name, cmd in apps_windows.items():
                if name in action:
                    os.startfile(cmd)  # Windows 專屬的開啟指令
                    return f"💻 已為您開啟應用程式：{name}"
            
            # 如果都不在清單內，嘗試當作一般指令執行看看 (防呆)
            return f"❌ 找不到名為 '{action}' 的內建快捷指令。您可以手動將它加入程式碼的字典中。"
            
        elif system_os == "Darwin": # macOS 邏輯
            # macOS 通常可以用 open -a "應用程式名稱"
            app_name = action.replace("打開", "").replace("開啟", "").strip()
            subprocess.Popen(["open", "-a", app_name])
            return f"💻 已嘗試在 Mac 上為您開啟：{app_name}"
            
        else:
            return "❌ 目前的開啟程式功能主要支援 Windows 與 macOS 系統。"

    except Exception as e:
        return f"開啟程式時發生錯誤: {str(e)}"