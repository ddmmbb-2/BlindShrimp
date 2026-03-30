import urllib.request
import urllib.parse
import json

SKILL_NAME = 'WIKI_SEARCH'
SKILL_DESC = '查詢維基百科上的精確名詞解釋、人物或歷史事件。Action 請填寫「要查詢的關鍵字」（例如：黑洞、相對論、周杰倫）。'

def execute(action, **kwargs):
    if not action:
        return "錯誤：請提供要查詢的關鍵字。"

    keyword = action.strip()
    
    try:
        # 將關鍵字轉為 URL 安全編碼
        encoded_kw = urllib.parse.quote(keyword)
        
        # 呼叫維基百科的免費摘要 API (zh 代表中文維基)
        url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{encoded_kw}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        extract = data.get('extract', '有找到頁面，但沒有文字摘要。')
        
        # 把精確的資料丟給大腦，讓它消化後講給使用者聽
        return f"📖 來自維基百科的可靠資料：\n【{keyword}】\n{extract}\n\n(提示：請將上述資料用自然、口語化的方式總結並回覆給使用者)"

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"❌ 維基百科上找不到關於「{keyword}」的精確條目，請嘗試更換同義詞。"
        return f"連線錯誤: {e}"
    except Exception as e:
        return f"查詢維基百科時發生錯誤: {str(e)}"