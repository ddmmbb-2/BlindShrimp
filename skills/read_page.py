import re
from playwright.sync_api import sync_playwright

SKILL_NAME = 'READ_PAGE'
SKILL_DESC = '讀取指定網頁的內文。請傳入完整的網址。'

def execute(action, **kwargs):
    url = action.strip()
    if not url.startswith('http'):
        return "錯誤：網址必須以 http 開頭。"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(15000)
            page.goto(url, wait_until="networkidle")
            text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', page.content(), flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            browser.close()

        # 回傳內容並明確標示
        return f"【已成功獲取網頁資料】：\n{text[:2000]}"
    except Exception as e:
        return f"讀取失敗: {str(e)}"