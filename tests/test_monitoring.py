def test_monitoring_dashboard_empty(client, auth_headers):
    response = client.get("/api/monitoring/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_owed_to"] == 0.0
    assert data["total_owed_by"] == 0.0
    assert data["current_balance"] == 0.0
    assert data["default_currency"] == "UZS"
    assert data["total_debts_count"] == 0


def test_monitoring_dashboard_calculations(client, auth_headers):
    """
    Berilgan qarzlar (owed_to): 200,000 + 300,000 = 500,000
    Olingan qarzlar (owed_by): 150,000
    Joriy balans (farqi): 500,000 - 150,000 = +350,000
    """
    # 1. Berilgan qarz
    client.post(
        "/api/debts/",
        json={"person_name": "Ali", "debt_type": "owed_to", "amount": 200000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    # 2. Yana berilgan qarz
    client.post(
        "/api/debts/",
        json={"person_name": "Vali", "debt_type": "owed_to", "amount": 300000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    # 3. Olingan qarz
    client.post(
        "/api/debts/",
        json={"person_name": "Gani", "debt_type": "owed_by", "amount": 150000.0, "currency": "UZS"},
        headers=auth_headers,
    )

    response = client.get("/api/monitoring/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_owed_to"] == 500000.0
    assert data["total_owed_by"] == 150000.0
    assert data["current_balance"] == 350000.0
    assert data["total_debts_count"] == 3
    assert data["active_debts_count"] == 3

    # Valyutalar bo'yicha breakdown
    uzs_breakdown = next((b for b in data["currency_breakdown"] if b["currency"] == "UZS"), None)
    assert uzs_breakdown is not None
    assert uzs_breakdown["total_owed_to"] == 500000.0
    assert uzs_breakdown["total_owed_by"] == 150000.0
    assert uzs_breakdown["net_balance"] == 350000.0


def test_monitoring_multi_currency(client, auth_headers):
    # UZS qarz
    client.post(
        "/api/debts/",
        json={"person_name": "Sardor", "debt_type": "owed_to", "amount": 1000000.0, "currency": "UZS"},
        headers=auth_headers,
    )
    # USD qarz
    client.post(
        "/api/debts/",
        json={"person_name": "John", "debt_type": "owed_to", "amount": 200.0, "currency": "USD"},
        headers=auth_headers,
    )

    response = client.get("/api/monitoring/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    currencies = [b["currency"] for b in data["currency_breakdown"]]
    assert "UZS" in currencies
    assert "USD" in currencies
