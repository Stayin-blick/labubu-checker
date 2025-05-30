import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Define the product URLs you want to check
PRODUCTS = [
    {
        "name": "Have a Seat",
        "url": "https://a.aliexpress.com/_EwHudxU"
    },
    {
        "name": "Exciting Macaron (UK)",
        "url": "https://a.aliexpress.com/_EzVOUR0"
    },
    {
        "name": "Exciting Macaron (EU)",
        "url": "https://a.aliexpress.com/_EjGj1Q2"
    },
    {
        "name": "Big into Energy",
        "url": "https://a.aliexpress.com/_EHppBho"
    },
    {
        "name": "Exciting Macaron (generic)",
        "url": "https://a.aliexpress.com/_ExrMoN8"
    },
    {
        "name": "Have a Seat Plush",
        "url": "https://m.popmart.com/gb/products/738/the-monsters-have-a-seat-vinyl-plush-blind-box"
    },
    {
        "name": "Tasty Macarons",
        "url": "https://m.popmart.com/gb/products/641/the-monsters-tasty-macarons-vinyl-face-blind-box"
    },
    {
        "name": "PopMart Homepage Listing",
        "url": "https://m.popmart.com/gb/products/1064"
    },
]

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def is_available(page_text):
    return not any(kw in page_text.lower() for kw in ["sold out", "unavailable", "out of stock"])

def check_product(product):
    try:
        response = requests.get(product["url"], timeout=10)
        response.raise_for_status()
        if is_available(response.text):
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 Check it out: {product['url']}")
    except Exception as e:
        send_telegram(f"⚠️ Error checking {product['name']}: {e}")

def run_checks():
    # Send the "is running" message once daily at 7:00 AM
    now = datetime.utcnow()  # GitHub Actions uses UTC
    if now.hour == 6 and now.minute < 15:  # Within the first 15-minute window of 7AM
        send_telegram("🕵️‍♂️ Labubu Stock Checker is running...")

    for product in PRODUCTS:
        check_product(product)

if __name__ == "__main__":
    run_checks()
