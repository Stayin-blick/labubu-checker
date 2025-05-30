import os
import requests

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    return response.json()

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Please set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID environment variables.")
    else:
        result = send_telegram("✅ Test message from your Labubu bot!")
        print(result)
