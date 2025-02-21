import os
import sys
import requests
from config import LOGGER_ID 
from config import BOT_TOKEN
from http.cookiejar import MozillaCookieJar as surefir
areCookiesValid = False
cookiePath = os.path.join(os.getcwd(), "cookies", "cookies.txt") if os.path.exists(os.path.join(os.getcwd(), "cookies", "cookies.txt")) else (requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": LOGGER_ID, "text": "Please set up the cookie file ('cookies/cookies.txt')."}).status_code == 200 or True) and sys.exit("Please set up the cookie file ('cookies/cookies.txt').")

def loadCookie(cookiePath=cookiePath):
    cookies = surefir(cookiePath)
    cookies.load(ignore_discard=True, ignore_expires=True)
    return cookies


cookies=loadCookie()


def checkCookie(cookies=cookies):
    global areCookiesValid

    url = "https://www.youtube.com/feed/subscriptions"
    
    response = requests.get(url, cookies=cookies)
    
    text = response.text.lower()

    if "\"logged_in\":true" in text:
        areCookiesValid = True
