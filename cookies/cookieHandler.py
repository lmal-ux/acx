import sys
import requests
from config import LOGGER_ID
from config import BOT_TOKEN
cookiePath = os.path.join(os.getcwd(), "cookies", "cookies.txt") if os.path.exists(os.path.join(os.getcwd(), "cookies", "cookies.txt")) else (requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": LOGGER_ID, "text": "Please set up the cookie file ('cookies/cookies.txt')."}).status_code == 200 or True) and sys.exit("Please set up the cookie file ('cookies/cookies.txt').")
cookies = {
    name: value
    for line in open(cookiePath)
    if line.strip() and not line.startswith("#")
    for parts in [line.strip().split("\t")]
    if len(parts) >= 7
    for domain, flag, path, secure, expiration, name, value in [parts]
}

url = "https://www.youtube.com/feed/subscriptions"
text = requests.get(url, cookies=cookies).text.lower()
urlt = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
params = {
    "chat_id": LOGGER_ID,
    "text": f"Cookies are not valid. Please update the cookies.\n__**ERROR**__\n",
    "parse_mode": "Markdown"
}
areCookiesValid = True if "\"logged_in\":true" in text else ((requests.get(urlt, params).status_code == 200) or (print("Failed to send notification: Cookies Aren't Valid") or True)) and sys.exit("Script stopped.")
