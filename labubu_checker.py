import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Define the product URLs you want to check
PRODUCTS = [
    {
        "name": "Aliexpress UK Have a Seat",
        "url": "https://a.aliexpress.com/_EwHudxU"
    },
    {
        "name": "Aliexpress UK Macaron",
        "url": "https://a.aliexpress.com/_EzVOUR0"
    },
    {
        "name": "Aliexpress EU Macaron",
        "url": "https://a.aliexpress.com/_EjGj1Q2"
    },
    {
        "name": "Aliexpress EU Big into Energy",
        "url": "https://a.aliexpress.com/_EHppBho"
    },
    {
        "name": "Aliexpress Exciting Macaron",
        "url": "https://a.aliexpress.com/_ExrMoN8"
    },
    {
        "name": "PopMart Have a Seat Plush",
        "url": "https://m.popmart.com/gb/products/738/the-monsters-have-a-seat-vinyl-plush-blind-box"
    },
    {
        "name": "PopMart Tasty Macarons",
        "url": "https://m.popmart.com/gb/products/641/the-monsters-tasty-macarons-vinyl-face-blind-box"
    },
    {
        "name": "PopMart Big into Energy",
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

def is_available(product_name: str, html: str) -> bool:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True).lower()

    # Generic out-of-stock phrases
    unavailable_phrases = [
        "notify me when available",
        "sorry, the product is currently unavailable for purchase",
        "currently unavailable",
        "out of stock"
    ]

    # Check for phrases first
    if any(phrase in text for phrase in unavailable_phrases):
        return False

    # Site-specific button or status logic
    if "aliexpress" in product_name.lower():
        # AliExpress: look for "Add to Cart" button or availability label
        return "add to cart" in text or "buy now" in text

    elif "popmart" in product_name.lower():
        # Pop Mart: look for "Add to Cart" or lack of "Notify me"
        return "add to cart" in text and "notify me" not in text

    # Default to False if uncertain
    return False

def check_product(product):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(product["url"], headers=headers, timeout=10)
        response.raise_for_status()

        if is_available(product['name'], response.text):
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 Check it out: {product['url']}")
        else:
            print(f"❌ Not available: {product['name']}")
    except Exception as e:
        send_telegram(f"⚠️ Error checking {product['name']}: {e}")

def run_checks():
    # Send the "is running" message once daily at 7:00 AM BST (6:00 UTC)
    now = datetime.utcnow()
    if now.hour == 6 and now.minute < 15:
        send_telegram("🕵️‍♂️ Labubu Stock Checker is running...")

    for product in PRODUCTS:
        check_product(product)

if __name__ == "__main__":
    run_checks()