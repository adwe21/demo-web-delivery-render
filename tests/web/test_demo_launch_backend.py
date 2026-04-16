from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from web.backend.app import DATA_FILE, app, store


client = TestClient(app)


def _restore_data_file(original: str) -> None:
    DATA_FILE.write_text(original, encoding="utf-8")


def test_healthcheck_reports_ok_and_intake_count() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "demo-launch-site-backend"
    assert payload["intakes_count"] == len(store.list())


def test_contract_summary_exposes_integration_endpoints() -> None:
    response = client.get("/api/contact-intakes/contract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["healthcheck"] == "GET /api/health"
    assert payload["submit_intake"] == "POST /api/contact-intakes"
    assert payload["list_intakes"] == "GET /api/contact-intakes"
    assert payload["request_example"]["source"] == "launch-page"


def test_create_contact_intake_persists_record() -> None:
    original = DATA_FILE.read_text(encoding="utf-8") if DATA_FILE.exists() else "[]\n"
    try:
        request_payload = {
            "name": "Jamie Rivera",
            "email": "jamie@acme.co",
            "company": "Acme Launches",
            "use_case": "Need a launch microsite to capture enterprise demo requests before our May campaign.",
            "source": "sales-demo",
        }

        response = client.post("/api/contact-intakes", json=request_payload)

        assert response.status_code == 201
        payload = response.json()
        assert payload["message"] == "Launch intake captured."
        assert payload["intake"]["email"] == "jamie@acme.co"
        assert payload["intake"]["status"] == "received"

        stored = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        assert any(item["id"] == payload["intake"]["id"] for item in stored)
    finally:
        _restore_data_file(original)


def test_create_contact_intake_rejects_invalid_email() -> None:
    response = client.post(
        "/api/contact-intakes",
        json={
            "name": "Bad Email",
            "email": "invalid-email",
            "company": "Broken Co",
            "use_case": "This request should fail validation because the email is malformed.",
            "source": "launch-page",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"][0]["msg"]
