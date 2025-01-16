import sys
from AnonXMusic.platforms.Youtube import cookiePath
from config import BOT_TOKEN as bot, LOGGER_ID as log  # Assuming config is in the same directory as the script
import requests

def load_cookies_from_file(file_path):
    cookies = {}
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue  # Skip comments and empty lines
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                domain, flag, path, secure, expiration, name, value = parts
                cookies[name] = value
    return cookies

def notify_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Notification sent to Telegram.")
        else:
            print(f"Failed to send notification. HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def check_youtube_cookies():
    # Use cookiePath as the path to the cookies.txt file
    cookies = load_cookies_from_file(cookiePath)

    # Test with a YouTube URL
    url = "https://www.youtube.com/feed/subscriptions"

    # Make the request with loaded cookies
    response = requests.get(url, cookies=cookies)

    # Check if cookies are valid
    if "Sign in" in response.text:
        print("Cookies are not valid.")
        # Notify via Telegram if cookies are not working
        notify_telegram(bot, log, "Cookies are not working. Please update the cookies.")
        # Gracefully stop the script after notifying
        sys.exit("Cookies are not valid. Script stopped.")
    else:
        print("Cookies are valid!")

# Automatically run the logic when the script is executed
check_youtube_cookies()
