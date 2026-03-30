import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json

# 【關鍵 1】：改變技能名稱與描述，讓 AI 認為這是真正的搜尋引擎
SKILL_NAME = 'WEB_SEARCH'
SKILL_DESC = '網頁搜尋引擎。當你需要查詢最新資訊、時事、名詞解釋或任何你不知道的事情時，請呼叫此技能。直接傳入搜尋「關鍵字」即可。'

def execute(action, **kwargs):
    keyword = action.strip()
    if not keyword:
        return "錯誤：請提供搜尋關鍵字。"

    results = []
    encoded_kw = urllib.parse.quote(keyword)
    # 偽裝成一般瀏覽器，避免被阻擋
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # ==========================================
    # 搜尋來源 1：維基百科 API (負責知識、名詞解釋、歷史)
    # ==========================================
    try:
        wiki_url = f"https://zh.wikipedia.org/w/api.php?action=opensearch&search={encoded_kw}&limit=2&format=json"
        req = urllib.request.Request(wiki_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            wiki_data = json.loads(response.read().decode('utf-8'))
            # API 回傳格式: [ "關鍵字", ["標題1"], ["摘要1"], ["網址1"] ]
            if len(wiki_data) >= 4 and wiki_data[1]:
                results.append("【百科與名詞解釋】")
                for i in range(len(wiki_data[1])):
                    title = wiki_data[1][i]
                    desc = wiki_data[2][i]
                    url = wiki_data[3][i] # 取得維基百科網址
                    if desc:
                        results.append(f"✦ {title}: {desc}\n  🔗網址: {url}")
    except Exception as e:
        print(f"Wiki 搜尋錯誤: {e}") # 內部除錯用，不干擾主程式

    # ==========================================
    # 搜尋來源 2：Google News RSS (負責時事、新聞、動態網頁內容)
    # ==========================================
    try:
        gn_url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
        req = urllib.request.Request(gn_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            root = ET.fromstring(response.read())
            items = root.findall('.//item')
            if items:
                # 如果前面有維基百科的結果，加個換行區隔
                if results:
                    results.append("") 
                results.append("【最新網頁資訊與時事】")
                # 取前 4 篇，確保 Token 不會爆掉
                for item in items[:4]:
                    title = item.find('title').text if item.find('title') is not None else '無標題'
                    pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else '' # 取得新聞網址
                    results.append(f"❖ {title} ({pubDate})\n  🔗網址: {link}")
    except Exception as e:
        print(f"RSS 搜尋錯誤: {e}")


# ==========================================
    # 搜尋來源 4：食尚玩家與專業美食 RSS
    # ==========================================
    try:
        # 食尚玩家官方 RSS 網址
        # 加上關鍵字搜尋 (Google News 橋接方式獲取食尚玩家內容)
        food_sources = [
            {
                "name": "食尚玩家",
                "url": f"https://news.google.com/rss/search?q={encoded_kw}+site:supertaste.tvbs.com.tw&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            },
            {
                "name": "WalkerLand 窩客島",
                "url": f"https://www.walkerland.com.tw/rss/tag/{encoded_kw}"
            }
        ]

        if results: results.append("") 
        results.append("【食尚玩家與在地美食推薦】")

        for source in food_sources:
            try:
                req = urllib.request.Request(source["url"], headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    root = ET.fromstring(response.read())
                    # Google News RSS 結構與一般 RSS 略有不同，但共通點是 <item>
                    items = root.findall('.//item')
                    
                    # 每個來源抓取前 3 篇
                    for item in items[:3]:
                        f_title = item.find('title').text if item.find('title') is not None else '無標題'
                        # 去掉標題後的來源字樣 (例如: - 食尚玩家)
                        f_title = f_title.split(' - ')[0] 
                        f_link = item.find('link').text if item.find('link') is not None else ''
                        
                        results.append(f"🍽️ [{source['name']}] {f_title}\n  🔗網址: {f_link}")
            except Exception as e:
                continue 
                
    except Exception as e:
        print(f"美食 RSS 錯誤: {e}")



    # ==========================================
    # 搜尋來源 3：YouTube 預設頻道 RSS (負責影音動態)
    # ==========================================
    try:
        # 將你想要監控的頻道 ID 放在這個陣列裡 (可隨時自由新增)
        yt_channel_ids = [
            "UCpu3bemTQwAU8PqM4FepqIg", # 公視新聞網 (時事)
            "UCgdwtyqBunlRb-i-7PnCssQ"  # 木棉花 Muse TW (動畫影音)
        ]
        
        if results: results.append("") 
        results.append("【預設 YouTube 頻道最新影片】")
        
        for ch_id in yt_channel_ids:
            yt_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}"
            req = urllib.request.Request(yt_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                root = ET.fromstring(response.read())
                
                # 自動抓取頻道名稱，讓 AI 知道這是誰發的影片
                author_elem = root.find('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                channel_name = author_elem.text if author_elem is not None else "未知頻道"
                
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                # 每個頻道抓取最新 2 部影片，避免洗版導致 Token 爆掉
                for entry in entries[:2]:
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    title = title_elem.text if title_elem is not None else '無標題'
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                    link = link_elem.attrib['href'] if link_elem is not None else '' # 取得影片網址
                    results.append(f"▶ [{channel_name}] {title}\n  🔗網址: {link}")
                    
    except Exception as e:
        print(f"YouTube RSS 錯誤: {e}")

    # ==========================================
    # 統整結果回傳給大腦
    # ==========================================
    if not results:
        return f"網頁搜尋找不到關於「{keyword}」的結果，請嘗試更換或簡化關鍵字。"

    # 將所有結果合併成單一字串
    final_output = f"以下是「{keyword}」的網頁搜尋結果：\n" + "\n".join(results)
    return final_output