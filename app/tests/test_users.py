import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.verify import get_current_user
import models
from main import app

# ✅ Override the auth dependency
def override_get_current_user():
    return models.User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hashed_password="x"
    )

# ✅ Apply the override before creating the client
@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)

# Optional: auth header mock (not needed unless your app checks header presence)
@pytest.fixture
def token():
    return "mock_jwt_token"

@pytest.fixture
def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# -------------------- TESTS --------------------

def test_list_users(client):
    res = client.get("/users/")
    assert res.status_code == 200
    assert "data" in res.json()
    assert "result" in res.json()["data"]

@patch("crud.get_user")
def test_get_user_success(mock_get_user, client):
    mock_get_user.return_value = models.User(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        hashed_password="x"
    )
    res = client.get("/users/1")
    assert res.status_code == 200
    data = res.json()
    assert "result" in data["data"]

@patch("crud.get_user")
def test_get_user_not_found(mock_get_user, client):
    mock_get_user.return_value = None
    res = client.get("/users/999")
    assert res.status_code == 404

@patch("crud.update_user")
def test_patch_user(mock_update_user, client):
    mock_update_user.return_value = models.User(id=1)
    res = client.patch("/users/1", json={"first_name": "New"})
    assert res.status_code == 200
    data = res.json()
    assert data["data"]["detail"] == "User details updated"

@patch("crud.delete_user")
def test_delete_user(mock_delete_user, client):
    mock_delete_user.return_value = True
    res = client.delete("/users/1")
    assert res.status_code == 200
    assert res.json()["data"] == "User deleted"
