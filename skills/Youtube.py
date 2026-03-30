import urllib.request
import urllib.parse
import re
import subprocess
import os
import platform

SKILL_NAME = 'YOUTUBE_PLAYER'
SKILL_DESC = '播放或關閉音樂。Action 請填寫歌名（如：周杰倫）來使用 yt-dlp 下載並以 VLC 播放；若要「關閉音樂/停止播放」請填寫 "STOP" 或 "關閉" 或 "停止" 等字眼。'

def execute(action, **kwargs):
    if not action:
        return "錯誤：請提供想聽的歌名或指令。"

    action = action.strip()
    system_os = platform.system() # 判斷作業系統

    # ==========================================
    # 邏輯 1：處理「關閉/停止音樂」的指令
    # ==========================================
    stop_keywords = ["stop", "關閉", "停止", "結束"]
    if action.lower() in stop_keywords:
        try:
            if system_os == "Windows":
                # 強制關閉 Windows 上的 VLC
                os.system("taskkill /F /IM vlc.exe /T")
                return "🛑 已強制關閉 VLC 播放器，音樂已停止。"
            elif system_os == "Darwin":
                # 強制關閉 macOS 上的 VLC
                os.system("pkill -f 'VLC'")
                return "🛑 已強制關閉 VLC 播放器，音樂已停止。"
            else:
                return "🛑 目前僅支援在 Windows/macOS 關閉 VLC。"
        except Exception as e:
            return f"關閉 VLC 時發生錯誤: {e}"

    # ==========================================
    # 邏輯 2：處理「搜尋、下載與播放音樂」的指令
    # ==========================================
    try:
        # 1. 將中文或空格轉換為 URL 編碼
        search_keyword = urllib.parse.quote(action)
        search_url = f"https://www.youtube.com/results?search_query={search_keyword}"
        
        # 2. 發送請求取得搜尋結果頁面
        req = urllib.request.Request(
            search_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        response = urllib.request.urlopen(req)
        html = response.read().decode()

        # 3. 找出第一個影片 ID
        video_ids = re.findall(r"watch\?v=(\S{11})", html)

        if not video_ids:
            return f"找不到關於 '{action}' 的影片。"

        first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        
        # 4. 呼叫 yt-dlp 下載影片
        # 使用 -f b (best) 抓取最佳單一檔案，並存成 temp_play.mp4，使用 --force-overwrites 每次覆寫同一個檔案避免塞滿硬碟
        download_file = "temp_play.mp4"
        print(f"📥 正在使用 yt-dlp 下載：{first_video_url}")
        
        # 呼叫 yt-dlp (注意：如果 yt-dlp 不在同目錄下或環境變數中，這裡會報錯)
        dl_process = subprocess.run(
            ["yt-dlp.exe", "-f", "b", "-o", download_file, "--force-overwrites", first_video_url],
            capture_output=True, text=True
        )
        
        if dl_process.returncode != 0:
            return f"下載失敗，yt-dlp 錯誤訊息: {dl_process.stderr[:200]}"

        # 5. 指定使用 VLC 開啟剛下載的檔案
        if system_os == "Windows":
            # 由於 VLC 安裝時通常不會自動加入系統 PATH，我們手動尋找常見的安裝路徑
            vlc_path = "vlc.exe" 
            if os.path.exists(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
                vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            elif os.path.exists(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"):
                vlc_path = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            
            subprocess.Popen([vlc_path, download_file])
        elif system_os == "Darwin":
            subprocess.Popen(["open", "-a", "VLC", download_file])
        else:
            subprocess.Popen(["vlc", download_file])
        
        return f"🎵 已下載完畢，正在使用 VLC 播放：{action}"

    except Exception as e:
        return f"播放出錯了: {str(e)}"