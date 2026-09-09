import datetime


def test_create_debt_owed_to(client, auth_headers):
    payload = {
        "person_name": "Tuychi aka",
        "debt_type": "owed_to",
        "amount": 27000.0,
        "currency": "UZS",
        "description": "Monro kafee, lavash",
        "is_paid": False,
        "reminder_enabled": True,
    }
    response = client.post("/api/debts/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["person_name"] == "Tuychi aka"
    assert data["debt_type"] == "owed_to"
    assert data["amount"] == 27000.0
    assert data["currency"] == "UZS"
    assert data["description"] == "Monro kafee, lavash"
    assert data["is_paid"] is False
    assert "id" in data


def test_create_debt_owed_by(client, auth_headers):
    payload = {
        "person_name": "Aziz",
        "debt_type": "owed_by",
        "amount": 50000.0,
        "currency": "UZS",
        "description": "Benzin uchun qarz",
        "is_paid": False,
    }
    response = client.post("/api/debts/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["person_name"] == "Aziz"
    assert data["debt_type"] == "owed_by"
    assert data["amount"] == 50000.0


def test_filter_debts_owed_to_and_owed_by(client, auth_headers):
    # Create owed_to
    client.post(
        "/api/debts/",
        json={"person_name": "Person A", "debt_type": "owed_to", "amount": 100000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    # Create owed_by
    client.post(
        "/api/debts/",
        json={"person_name": "Person B", "debt_type": "owed_by", "amount": 40000.0, "currency": "UZS"},
        headers=auth_headers,
    )

    # Filter owed_to
    res_owed_to = client.get("/api/debts/?debt_type=owed_to", headers=auth_headers)
    assert res_owed_to.status_code == 200
    items_owed_to = res_owed_to.json()
    assert len(items_owed_to) >= 1
    assert all(item["debt_type"] == "owed_to" for item in items_owed_to)

    # Filter owed_by
    res_owed_by = client.get("/api/debts/?debt_type=owed_by", headers=auth_headers)
    assert res_owed_by.status_code == 200
    items_owed_by = res_owed_by.json()
    assert len(items_owed_by) >= 1
    assert all(item["debt_type"] == "owed_by" for item in items_owed_by)


def test_individual_debts_aggregation(client, auth_headers):
    """
    Test individual debt aggregation:
    Masalan: Azamat
    To Me: 1100000
    By Me: 1786000
    Net Balance: -686000
    """
    # Berilgan qarz (To Me)
    client.post(
        "/api/debts/",
        json={"person_name": "Azamat", "debt_type": "owed_to", "amount": 1100000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    # Olingan qarz (By Me)
    client.post(
        "/api/debts/",
        json={"person_name": "Azamat", "debt_type": "owed_by", "amount": 1786000.0, "currency": "UZS"},
        headers=auth_headers,
    )

    response = client.get("/api/debts/?debt_type=individual", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Azamat bo'yicha hisobotni topish
    azamat = next((item for item in data if item["person_name"] == "Azamat"), None)
    assert azamat is not None
    assert azamat["total_owed_to"] == 1100000.0
    assert azamat["total_owed_by"] == 1786000.0
    assert azamat["net_balance"] == -686000.0
    assert azamat["debts_count"] == 2


def test_update_debt(client, auth_headers):
    # Qarz yaratish
    create_res = client.post(
        "/api/debts/",
        json={"person_name": "Besulton", "debt_type": "owed_to", "amount": 80000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    debt_id = create_res.json()["id"]

    # Qarzni yangilash (PUT/PATCH)
    update_payload = {
        "amount": 95000.0,
        "is_paid": True,
        "description": "To'liq qaytarildi",
    }
    update_res = client.put(f"/api/debts/{debt_id}", json=update_payload, headers=auth_headers)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["amount"] == 95000.0
    assert updated_data["is_paid"] is True
    assert updated_data["description"] == "To'liq qaytarildi"


def test_delete_debt(client, auth_headers):
    create_res = client.post(
        "/api/debts/",
        json={"person_name": "Botir", "debt_type": "owed_by", "amount": 179000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    debt_id = create_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/debts/{debt_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Verify not found
    get_res = client.get(f"/api/debts/{debt_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_debt_security_isolation(client, auth_headers, second_auth_headers):
    # User 1 creates a debt
    create_res = client.post(
        "/api/debts/",
        json={"person_name": "Private Person", "debt_type": "owed_to", "amount": 500000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    debt_id = create_res.json()["id"]

    # User 2 tries to access User 1's debt -> 404
    get_res = client.get(f"/api/debts/{debt_id}", headers=second_auth_headers)
    assert get_res.status_code == 404

    # User 2 tries to delete User 1's debt -> 404
    del_res = client.delete(f"/api/debts/{debt_id}", headers=second_auth_headers)
    assert del_res.status_code == 404
