import urllib.request, urllib.error

paths = [
    "/",
    "/auth/login",
    "/dashboard",
    "/api/v1/status",
    "/api/v1/modules",
    "/api/v1/dashboard/session",
]

for p in paths:
    url = "http://127.0.0.1:8010" + p
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "sigmatest/1.0", "Accept": "text/html,application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            body = resp.read(400)
            print(f"GET {p} -> {code}")
            print(body.decode("utf-8", errors="replace")[:400])
    except urllib.error.HTTPError as e:
        data = e.read(400)
        print(f"GET {p} -> HTTPError {e.code}")
        print(data.decode("utf-8", errors="replace")[:400])
    except Exception as e:
        print(f"GET {p} -> ERROR: {e}")
    print("\n" + "-" * 60 + "\n")
