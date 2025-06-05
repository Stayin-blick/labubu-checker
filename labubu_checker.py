from playwright.sync_api import sync_playwright
import os
import requests
import time

PRODUCTS = [
    {
        "name": "Aliexpress Big into Energy",
        "url": "https://www.aliexpress.com/item/1005008878463323.html?srcSns=sns_SMS&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61134754237&aff_fcid=c210f1b338c142c4b838cae6b7d32c85-1749103432482-05336-_EJik2KA&tt=MG&aff_fsk=_EJik2KA&aff_platform=default&sk=_EJik2KA&aff_trace_key=c210f1b338c142c4b838cae6b7d32c85-1749103432482-05336-_EJik2KA&shareId=61134754237&businessType=ProductDetail&platform=AE&terminal_id=d1758cbb0a8e4d259cf93f989d130cfd&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress UK Big into Energy",
        "url": "https://www.aliexpress.com/item/1005008883462026.html?srcSns=sns_SMS&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61123262517&aff_fcid=3798a20c89a542f3b18abc7ddc46cbb5-1749103563242-00076-_EuwpFIw&tt=MG&aff_fsk=_EuwpFIw&aff_platform=default&sk=_EuwpFIw&aff_trace_key=3798a20c89a542f3b18abc7ddc46cbb5-1749103563242-00076-_EuwpFIw&shareId=61123262517&businessType=ProductDetail&platform=AE&terminal_id=d1758cbb0a8e4d259cf93f989d130cfd&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress UK Macaron",
        "url": "https://www.aliexpress.com/item/1005007966229736.html"
    },
    {
        "name": "Aliexpress Macaron",
        "url": "https://www.aliexpress.com/item/1005006169948468.html?srcSns=sns_SMS&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61130344529&aff_fcid=5a3bf270ed64485789101016560fd633-1749103673598-02101-_EIV6Wam&tt=MG&aff_fsk=_EIV6Wam&aff_platform=default&sk=_EIV6Wam&aff_trace_key=5a3bf270ed64485789101016560fd633-1749103673598-02101-_EIV6Wam&shareId=61130344529&businessType=ProductDetail&platform=AE&terminal_id=d1758cbb0a8e4d259cf93f989d130cfd&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress UK Have a Seat Plush",
        "url": "https://www.aliexpress.com/item/1005007966773739.html?srcSns=sns_SMS&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61126916350&aff_fcid=6d791d01ffc54e2998689a4742e8cac1-1749103845884-04137-_EHos8Am&tt=MG&aff_fsk=_EHos8Am&aff_platform=default&sk=_EHos8Am&aff_trace_key=6d791d01ffc54e2998689a4742e8cac1-1749103845884-04137-_EHos8Am&shareId=61126916350&businessType=ProductDetail&platform=AE&terminal_id=d1758cbb0a8e4d259cf93f989d130cfd&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress Have a Seat Plush",
        "url": "https://www.aliexpress.com/item/1005006169948468.html"
    },
    {
        "name": "PopMart Have a Seat Plush",
        "url": "https://www.aliexpress.com/item/1005007350029637.html?srcSns=sns_SMS&spreadType=socialShare&bizType=ProductDetail&social_params=61134759194&aff_fcid=a35da08c8ca44604ab1147aaab601796-1749103901339-00398-_ExiMejg&tt=MG&aff_fsk=_ExiMejg&aff_platform=default&sk=_ExiMejg&aff_trace_key=a35da08c8ca44604ab1147aaab601796-1749103901339-00398-_ExiMejg&shareId=61134759194&businessType=ProductDetail&platform=AE&terminal_id=d1758cbb0a8e4d259cf93f989d130cfd&afSmartRedirect=y"
    },
    {
        "name": "PopMart Tasty Macarons",
        "url": "https://www.popmart.com/gb/products/641/the-monsters-tasty-macarons-vinyl-face-blind-box"
    },
    {
        "name": "PopMart Big into Energy",
        "url": "https://www.popmart.com/gb/products/1064"
    },
]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Telegram API returned status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"⚠️ Error sending Telegram message: {e}")

def is_available(page_text: str, url: str) -> bool:
    text = page_text.lower()

    if "popmart.com" in url:
        if "notify me when available" in text or "notify me when in stock" in text:
            return False
        if "add to cart" in text or "buy now" in text:
            return True
        return False

    # AliExpress and others
    unavailable_phrases = [
        "notify me when available",
        "sorry, the product is currently unavailable for purchase",
        "out of stock",
        "currently unavailable",
        "sold out",
        "temporarily out of stock",
        "find similar",
        "Sorry, this item is no longer available!",
    ]

    if "add to cart" not in text and "buy now" not in text and "add to basket" not in text:
        return False

    return not any(phrase in text for phrase in unavailable_phrases)

def check_product(playwright, product):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    ))
    page = context.new_page()

    try:
        print(f"🔍 Checking: {product['name']}")
        page.goto(product["url"], wait_until="domcontentloaded", timeout=30000)
        time.sleep(20)  # Give JS time to settle

        page_text = page.content()
        if is_available(page_text, product["url"]):
            print(f"✅ {product['name']} is in stock.")
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 [Buy here]({product['url']})")
        else:
            print(f"❌ {product['name']} is still sold out.")
            send_telegram(f"❌ *{product['name']}* is still sold out.")  # <-- Added here
    except Exception as e:
        print(f"❗️Error checking {product['name']}: {e}")
        send_telegram(f"⚠️ Error checking *{product['name']}*: {e}")
    finally:
        browser.close()

def run():
    with sync_playwright() as p:
        for product in PRODUCTS:
            check_product(p, product)

if __name__ == "__main__":
    run()
