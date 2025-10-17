import pytest
from unittest.mock import patch
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def token():
    reg = client.post("/auth/register", json={
        "first_name": "Jane", "last_name": "Doe",
        "email": "jane@example.com", "password": "strongpass"
    })
    login = client.post("/auth/login", json={"email": "jane@example.com", "password": "strongpass"})
    return login.json()["data"]["access_token"]



@patch("app.usda.service.get_best_calorie_for_dish")
def test_get_calories_success(mock_usda, token):
    mock_usda.return_value = {
        "calories_per_unit": 100.0,
        "raw": {"ingredients": "rice, salt"}
    }
    payload = {"dish_name": "Rice", "servings": 2}
    res = client.post("/calories/get-calories", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_calories"] == 712.0

@patch("app.usda.service.get_best_calorie_for_dish")
def test_get_calories_not_found(mock_usda, client, token):
    mock_usda.return_value = None
    payload = {"dish_name": "unknown", "servings": 1}
    res = client.post("/calories/get-calories", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
