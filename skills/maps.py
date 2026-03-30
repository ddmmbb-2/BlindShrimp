import urllib.parse
import webbrowser  # 控制瀏覽器的核心套件

SKILL_NAME = 'MAP_SEARCH'
SKILL_DESC = '在地圖上尋找特定地點、餐廳或店家。Action 請填寫要搜尋的地點或關鍵字（例如：台北車站附近的牛肉麵、台中文心森林公園、信義區星巴克）。'

def execute(action, **kwargs):
    if not action:
        return "錯誤：請提供想要搜尋的地點或餐廳名稱。"

    try:
        search_keyword = urllib.parse.quote(action)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={search_keyword}"
        
        # 【關鍵修改】：這一行會自動呼叫你電腦的「預設瀏覽器」
        webbrowser.open(maps_url)

        return f"📍 已經成功在 Google 地圖上為您搜尋：{action}\n網址：{maps_url}"

    except Exception as e:
        return f"開啟地圖時發生錯誤: {str(e)}"