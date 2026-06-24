import re
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

base = "https://call-pike-mechanical-reasoning.trycloudflare.com"
cj = CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
login = base + "/login/"
html = op.open(login, timeout=30).read().decode()
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1)
data = urllib.parse.urlencode(
    {"username": "admin", "password": "Admin@12345", "csrfmiddlewaretoken": csrf}
).encode()
req = urllib.request.Request(login, data=data, method="POST")
req.add_header("Referer", login)
req.add_header("Origin", base)
try:
    op.open(req, timeout=30)
    dash = op.open(base + "/", timeout=30).read().decode()
    print("login OK" if "hero-advanced" in dash else "login FAIL - no hero")
except Exception as exc:
    print("login FAIL", exc)
