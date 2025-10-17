import pytest
from unittest.mock import patch
import models

def test_register_user(client):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "strongpass"
    }
    res = client.post("/auth/register", json=payload)
    data = res.json()
    assert "id" in data["data"]
    assert data["data"]["message"] == "Registered successfully."
    assert data["status"] == "GS20101"

def test_register_duplicate_email(client):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "anotherpass"
    }
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 400
    assert "Email already registered" in res.text

def test_login_success(client):
    payload = {"email": "john@example.com", "password": "strongpass"}
    res = client.post("/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data["data"]

def test_login_invalid_credentials(client):
    payload = {"email": "john@example.com", "password": "wrongpass"}
    res = client.post("/auth/login", json=payload)
    assert res.status_code == 401
    assert "Invalid credentials" in res.text