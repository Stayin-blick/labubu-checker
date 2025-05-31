from playwright.sync_api import sync_playwright
import os
import requests
import time

PRODUCTS = [
    {
        "name": "Aliexpress UK Have a Seat",
        "url": "https://www.aliexpress.com/item/1005007966773739.html"
    },
    {
        "name": "Aliexpress UK Macaron",
        "url": "https://www.aliexpress.com/item/1005007966229736.html"
    },
    {
        "name": "Aliexpress EU Macaron",
        "url": "https://www.aliexpress.com/item/1005008117007093.html"
    },
    {
        "name": "Aliexpress EU Big into Energy",
        "url": "https://www.aliexpress.com/item/1005008886096545.html"
    },
    {
        "name": "Aliexpress Exciting Macaron",
        "url": "https://www.aliexpress.com/item/1005006169948468.html"
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
