import os
import sys
import requests
from config import LOGGER_ID 
from config import BOT_TOKEN
from http.cookiejar import MozillaCookieJar as surefir
cookiePath = os.path.join(os.getcwd(), "cookies", "cookies.txt")

def loadCookie(cookiePath=cookiePath):
    if not os.path.exists(cookiePath):
      raise FileNotFoundError("The specified file was not found.")
    cookies = surefir(cookiePath)
    cookies.load(ignore_discard=True, ignore_expires=True)
    return cookies
  
def checkCookie(cookiePath=cookiePath):
    
    cookies=loadCookie(cookiePath)

    url = "https://www.youtube.com/feed/subscriptions"
    tries=0
    while tries<=3:
      text = requests.get(url, cookies=cookies).text.lower()
      if "\"logged_in\":true" in text:
        return True
      tries+=1
      print("areCookiesValid:-", areCookiesValid ,f"-- tries:- {tries}")
    return False

areCookiesValid = checkCookie()
