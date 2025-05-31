from playwright.sync_api import sync_playwright
import os
import requests
import time

PRODUCTS = [
    {
        "name": "Aliexpress UK Have a Seat",
        "url": "https://www.aliexpress.com/item/1005007966773739.html?srcSns=sns_Copy&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61114524894&aff_fcid=c044fe1cf0a844b0a8299cfef651abdd-1748677413314-04002-_EwHudxU&tt=MG&aff_fsk=_EwHudxU&aff_platform=default&sk=_EwHudxU&aff_trace_key=c044fe1cf0a844b0a8299cfef651abdd-1748677413314-04002-_EwHudxU&shareId=61114524894&businessType=ProductDetail&platform=AE&terminal_id=24e542db40a34d0da57362870af2d154&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress UK Macaron",
        "url": "https://www.aliexpress.com/item/1005007966229736.html?srcSns=sns_Copy&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61114524965&aff_fcid=8d16cab76a044210b988b5e0d5ae052a-1748677439908-00843-_EzVOUR0&tt=MG&aff_fsk=_EzVOUR0&aff_platform=default&sk=_EzVOUR0&aff_trace_key=8d16cab76a044210b988b5e0d5ae052a-1748677439908-00843-_EzVOUR0&shareId=61114524965&businessType=ProductDetail&platform=AE&terminal_id=24e542db40a34d0da57362870af2d154&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress EU Macaron",
        "url": "https://www.aliexpress.com/item/1005008117007093.html?srcSns=sns_Copy&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61121514970&aff_fcid=9406f5db448544f98fa5348ae37ffee8-1748677465791-06925-_EjGj1Q2&tt=MG&aff_fsk=_EjGj1Q2&aff_platform=default&sk=_EjGj1Q2&aff_trace_key=9406f5db448544f98fa5348ae37ffee8-1748677465791-06925-_EjGj1Q2&shareId=61121514970&businessType=ProductDetail&platform=AE&terminal_id=24e542db40a34d0da57362870af2d154&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress EU Big into Energy",
        "url": "https://www.aliexpress.com/item/1005008886096545.html?srcSns=sns_Copy&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61114526438&aff_fcid=7fe148e119b842f5bb68a5c3b16e4e88-1748677486289-01305-_EHppBho&tt=MG&aff_fsk=_EHppBho&aff_platform=default&sk=_EHppBho&aff_trace_key=7fe148e119b842f5bb68a5c3b16e4e88-1748677486289-01305-_EHppBho&shareId=61114526438&businessType=ProductDetail&platform=AE&terminal_id=24e542db40a34d0da57362870af2d154&afSmartRedirect=y"
    },
    {
        "name": "Aliexpress Exciting Macaron",
        "url": "https://www.aliexpress.com/item/1005006169948468.html?srcSns=sns_Copy&sourceType=1&spreadType=socialShare&bizType=ProductDetail&social_params=61114526499&aff_fcid=4fa4c8da32f64c09800cd0081053e28f-1748677501907-05677-_ExrMoN8&tt=MG&aff_fsk=_ExrMoN8&aff_platform=default&sk=_ExrMoN8&aff_trace_key=4fa4c8da32f64c09800cd0081053e28f-1748677501907-05677-_ExrMoN8&shareId=61114526499&businessType=ProductDetail&platform=AE&terminal_id=24e542db40a34d0da57362870af2d154&afSmartRedirect=y"
    },
    {
        "name": "PopMart Have a Seat Plush",
        "url": "https://www.popmart.com/gb/products/738/the-monsters-have-a-seat-vinyl-plush-blind-box"
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

def is_available(page_text: str) -> bool:
    unavailable_phrases = [
        "notify me when available",
        "sorry, the product is currently unavailable for purchase",
        "out of stock",
        "currently unavailable",
        "sold out",
        "temporarily out of stock",
        "find similar",
    ]
    text = page_text.lower()

    # Ensure some sign of a real product page before checking stock
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
        page.goto(product["url"], wait_until="networkidle", timeout=30000)
        time.sleep(3)  # Allow JS to settle

        page_text = page.content()
        if is_available(page_text):
            print(f"✅ {product['name']} is in stock.")
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 [Buy here]({product['url']})")
        else:
            print(f"❌ {product['name']} is still sold out.")
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
