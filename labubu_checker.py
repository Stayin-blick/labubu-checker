import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# List of products to track
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

# Telegram configuration
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(message):
    """Send a message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")

def is_available(page_text: str) -> bool:
    """Check if item is available based on common 'out of stock' phrases"""
    unavailable_phrases = [
        "Notify me when available",
        "Sorry, the product is currently unavailable for purchase",
        "Out of stock",
        "Currently unavailable",
        "Sold out",
        "Temporarily out of stock",
        "Find Similar",
    ]
    text = page_text.lower()
    return not any(phrase.lower() in text for phrase in unavailable_phrases)

def check_product(product):
    try:
        response = requests.get(product["url"], timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        if is_available(text):
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 [Buy here]({product['url']})")
    except Exception as e:
        send_telegram(f"⚠️ Error checking *{product['name']}*: {e}")

def run_checks():
    now = datetime.utcnow()
    if now.hour == 7 and now.minute < 15:
        send_telegram("🕵️‍♂️ Labubu Stock Checker is running (daily check-in at 7AM UTC)...")

    for product in PRODUCTS:
        check_product(product)

if __name__ == "__main__":
    run_checks()
