def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "john_doe",
            "email": "john@example.com",
            "password": "strongpassword123",
            "full_name": "John Doe",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "john_doe"
    assert data["email"] == "john@example.com"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_username_fails(client):
    user_payload = {
        "username": "duplicate_user",
        "email": "dup1@example.com",
        "password": "password123",
    }
    res1 = client.post("/api/auth/register", json=user_payload)
    assert res1.status_code == 201

    user_payload2 = {
        "username": "duplicate_user",
        "email": "dup2@example.com",
        "password": "password123",
    }
    res2 = client.post("/api/auth/register", json=user_payload2)
    assert res2.status_code == 400
    assert "band" in res2.json()["detail"].lower()


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"username": "bob", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"


def test_get_current_user_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
