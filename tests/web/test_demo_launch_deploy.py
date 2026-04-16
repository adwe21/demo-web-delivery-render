from __future__ import annotations

from fastapi.testclient import TestClient

from web.backend.deploy_app import app


client = TestClient(app)


def test_deploy_app_serves_index_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert '<div id="root"></div>' in response.text
    assert '/assets/' in response.text


def test_deploy_app_exposes_backend_api_routes() -> None:
    health = client.get("/api/health")
    contract = client.get("/api/contact-intakes/contract")

    assert health.status_code == 200
    assert contract.status_code == 200
    assert contract.json()["submit_intake"] == "POST /api/contact-intakes"
