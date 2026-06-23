import re
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

base = "https://school-management-system-0xaa.onrender.com"
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
login_url = base + "/login/"
html = opener.open(login_url, timeout=60).read().decode()
print("login status ok")
print("css on login:", "style.css?v=" in html, re.search(r"style\.css\?v=([^\"']+)", html))
print("demo hint:", "Demo login" in html)
print("show_demo:", "show_demo" in html)
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
csrf = m.group(1)
data = urllib.parse.urlencode({"username": "admin", "password": "Admin@12345", "csrfmiddlewaretoken": csrf}).encode()
req = urllib.request.Request(login_url, data=data, method="POST")
req.add_header("Referer", login_url)
req.add_header("Content-Type", "application/x-www-form-urlencoded")
try:
    opener.open(req, timeout=60)
    print("login post ok")
except Exception as e:
    print("login post fail", e)
dash = opener.open(base + "/", timeout=60).read().decode()
print("dash len", len(dash))
for token in ["Unified", "stat-card-link", "stat-card-pro", "hero-advanced", "style.css?v=", "Active classes", "Classes &amp; courses", "Classes & courses"]:
    print(token, token.replace("&amp;", "&") in dash or token in dash)
print("first 500 chars of dash body snippet:")
idx = dash.find("main-content")
print(dash[idx:idx+800] if idx >= 0 else dash[:800])
