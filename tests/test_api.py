from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_endpoint():
    response = client.get("/api/add?a=2&b=3")
    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.1"}


def test_divide_by_zero_endpoint():
    response = client.get("/api/divide?a=10&b=0")
    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot divide by zero"}