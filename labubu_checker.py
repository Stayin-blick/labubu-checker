from playwright.sync_api import sync_playwright
import os
import requests
import time
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

# Telegram credentials from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """Send a message to a Telegram chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Telegram error: {e}")

def is_available(page_text: str) -> bool:
    """Check if product is available based on known 'sold out' phrases"""
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

def check_product(page, product):
    """Open product page and check for availability"""
    try:
        print(f"🔍 Checking: {product['name']}")
        page.goto(product["url"], timeout=30000, wait_until="networkidle")
        page_text = page.content()

        if is_available(page_text):
            send_telegram(f"🧸 *{product['name']}* is available!\n💷 [Buy here]({product['url']})")
        else:
            print(f"❌ {product['name']} is still sold out.")
    except Exception as e:
        send_telegram(f"⚠️ Error checking *{product['name']}*: {e}")

def run():
    now = datetime.utcnow()
    if now.hour == 6 and now.minute < 15:
        send_telegram("🕵️‍♂️ Labubu Stock Checker is running (daily check-in at 7AM BST)...")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for product in PRODUCTS:
            check_product(page, product)
            time.sleep(2)  # brief delay to reduce detection risk

        browser.close()

if __name__ == "__main__":
    run()
