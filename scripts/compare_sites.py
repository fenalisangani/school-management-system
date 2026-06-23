import re
import sys
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar


def check(name, base):
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    login_url = base.rstrip("/") + "/login/"
    try:
        html = opener.open(login_url, timeout=30).read().decode()
        m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
        if not m:
            print(f"{name}: ERROR no csrf")
            return
        csrf = m.group(1)
        data = urllib.parse.urlencode(
            {"username": "admin", "password": "Admin@12345", "csrfmiddlewaretoken": csrf}
        ).encode()
        req = urllib.request.Request(login_url, data=data, method="POST")
        req.add_header("Referer", login_url)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        opener.open(req, timeout=30)
        dash = opener.open(base.rstrip("/") + "/", timeout=30).read().decode()
        css = re.search(r"style\.css\?v=([^\"']+)", dash)
        ui = re.search(r'name="app-ui-version" content="([^"]+)"', dash)
        print(
            f"{name}: css={(css.group(1) if css else 'none')}",
            f"ui={(ui.group(1) if ui else 'old')}",
            f"hero={'hero-advanced' in dash}",
            f"stat-link={'stat-card-link' in dash}",
            f"old-cmd={'Command Center' in dash}",
            sep=" | ",
        )
    except Exception as exc:
        print(f"{name}: ERROR {exc}")


if __name__ == "__main__":
    check("local", "http://127.0.0.1:8765")
    check("tunnel", "https://call-pike-mechanical-reasoning.trycloudflare.com")
    check("render", "https://school-management-system-0xaa.onrender.com")
