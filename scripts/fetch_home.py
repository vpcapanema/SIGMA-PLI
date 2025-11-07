import sys
import urllib.request

req = urllib.request.Request(
    "http://127.0.0.1:8010/",
    headers={"User-Agent": "sigmatest/1.0", "Accept": "text/html"},
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        print(body)
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)
