from fastapi.testclient import TestClient

from app.main import app


def test_root_has_features():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "features" in response.json()
