from fastapi.testclient import TestClient
import app.main as m

client = TestClient(m.app)
resp = client.post(
    "/api/v1/auth/login", json={"identifier": "joao.silva", "password": "sigma123"}
)
print("status", resp.status_code)
print("body", resp.text)
print("cookies", resp.cookies)
