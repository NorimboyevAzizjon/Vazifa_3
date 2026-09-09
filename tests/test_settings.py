def test_get_default_settings(client, auth_headers):
    response = client.get("/api/settings/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["default_currency"] == "UZS"
    assert data["reminder_time"] == "09:00"
    assert data["reminder_days_before"] == 1
    assert data["notifications_enabled"] is True


def test_update_settings_put(client, auth_headers):
    payload = {
        "default_currency": "USD",
        "reminder_time": "18:30",
        "reminder_days_before": 3,
        "notifications_enabled": False,
    }
    response = client.put("/api/settings/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["default_currency"] == "USD"
    assert data["reminder_time"] == "18:30"
    assert data["reminder_days_before"] == 3
    assert data["notifications_enabled"] is False


def test_update_settings_patch(client, auth_headers):
    payload = {"default_currency": "EUR"}
    response = client.patch("/api/settings/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["default_currency"] == "EUR"
    # Other fields remain intact
    assert data["reminder_time"] == "09:00"


def test_settings_unauthorized(client):
    response = client.get("/api/settings/")
    assert response.status_code == 401
