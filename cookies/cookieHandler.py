import sys
import requests
from AnonXMusic.platforms import cookiePath
from config import LOGGER_ID
from config import BOT_TOKEN

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
    "text": f"Cookies are not valid. Please update the cookies.\n__**ERROR**__\n `{text[:3000] if len(text) > 3000 else text }`",
    "parse_mode": "Markdown"
}
areCookiesValid = True if "sign in" not in text and (print('Cookies are valid') or True) else (requests.get(urlt, params).status_code == 200 or (print("Failed to send notification: Cookies Aren't Valid") or True) and sys.exit("Script stopped."))
