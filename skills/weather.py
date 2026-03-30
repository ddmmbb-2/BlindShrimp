import urllib.request
import urllib.parse
import json

SKILL_NAME = 'WEATHER'
SKILL_DESC = '查詢指定地點的「目前即時」與「明天」天氣預報。Action 請直接填寫「地點名稱」（例如：台北、台中、Tokyo）。'

def execute(action, **kwargs):
    if not action:
        return "錯誤：請提供要查詢天氣的地點。"

    # 簡單過濾：預防 AI 把「台北 明天」整個當成地點傳進來，我們清掉多餘字眼
    location = action.replace("明天", "").replace("今天", "").replace("天氣", "").strip()
    # 如果清空後沒東西，就退回原始輸入
    if not location:
        location = action.strip()
    
    try:
        # 將地點轉換為 URL 安全的格式
        encoded_location = urllib.parse.quote(location)
        
        # 使用 ?format=j1 取得包含未來預報的完整 JSON 資料
        url = f"https://wttr.in/{encoded_location}?format=j1"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        # --- 1. 抓取目前即時天氣 ---
        current = data['current_condition'][0]
        curr_temp = current['temp_C']
        curr_desc = current['weatherDesc'][0]['value']  # 這裡是英文描述
        
        # --- 2. 抓取明天天氣預報 ---
        # data['weather'] 是一個陣列，[0]是今天，[1]是明天，[2]是後天
        tomorrow = data['weather'][1]
        tom_date = tomorrow['date']
        tom_max = tomorrow['maxtempC']
        tom_min = tomorrow['mintempC']
        # 取明天中午 (12:00) 的天氣狀態 (hourly 陣列每 3 小時一筆，[4] 大約是中午)
        tom_desc = tomorrow['hourly'][4]['weatherDesc'][0]['value'] 

        # 組合資訊，並在結尾加上一個小提示，請 AI 自己當翻譯官
        result = (
            f"以下為【{location}】的氣象數據：\n"
            f"📍 目前即時：{curr_desc}，氣溫 {curr_temp}°C\n"
            f"📅 明天 ({tom_date}) 預報：{tom_desc}，氣溫 {tom_min}°C ~ {tom_max}°C\n"
            f"（請將上述的英文天氣描述翻譯成自然、口語化的繁體中文來回覆使用者。）"
        )
        return result

    except Exception as e:
        return f"❌ 查詢天氣時發生錯誤: 找不到地點或連線失敗 ({str(e)})"