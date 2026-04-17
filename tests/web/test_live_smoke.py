from __future__ import annotations

from fastapi.testclient import TestClient
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from web.backend.deploy_app import app
from web.backend.smoke import SmokeCheckError, run_smoke_check


client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[2]
VALID_HTML = """
<!doctype html>
<html>
  <head>
    <title>Demo Launch Site</title>
    <link rel="canonical" href="https://demo-web-delivery.zeabur.app/" />
    <meta name="theme-color" content="#111827" />
    <meta property="og:title" content="Demo Launch Site" />
    <meta property="og:url" content="https://demo-web-delivery.zeabur.app/" />
    <meta property="og:image" content="https://demo-web-delivery.zeabur.app/og-image.svg" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Demo Launch Site" />
    <meta name="twitter:image" content="https://demo-web-delivery.zeabur.app/og-image.svg" />
  </head>
  <body></body>
</html>
"""


def _send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
    response = client.request(method, path, json=payload)
    content_type = response.headers.get("content-type")
    try:
        data = response.json()
    except Exception:
        data = None
    return response.status_code, response.text, data, content_type


def test_live_smoke_check_covers_root_health_and_contact_submission() -> None:
    report = run_smoke_check(_send)

    assert report["root_status"] == 200
    assert report["health_status"] == 200
    assert report["submit_status"] == 201
    assert report["list_status"] == 200
    assert report["submitted_email"] in report["listed_emails"]
    assert report["service"] == "demo-launch-site-backend"
    assert report["metadata_checks"] == {
        "title_ok": True,
        "canonical_ok": True,
        "theme_color_ok": True,
        "og_title_ok": True,
        "og_url_ok": True,
        "og_image_ok": True,
        "twitter_card_ok": True,
        "twitter_title_ok": True,
        "twitter_image_ok": True,
    }


def test_live_smoke_reports_frontend_failure_class() -> None:
    def failing_send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
        if path == "/":
            return 503, '{"detail":"frontend build not found"}', {"detail": "frontend build not found"}, "application/json"
        raise AssertionError(f"unexpected path: {path}")

    try:
        run_smoke_check(failing_send)
    except SmokeCheckError as exc:
        assert exc.failure_class == "frontend_unavailable"
        assert "frontend build not found" in exc.detail
    else:
        raise AssertionError("expected SmokeCheckError")


def test_live_smoke_reports_api_failure_class() -> None:
    def failing_send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
        if path == "/":
            return 200, VALID_HTML, None, "text/html"
        if path == "/api/health":
            return 500, '{"detail":"db offline"}', {"detail": "db offline"}, "application/json"
        raise AssertionError(f"unexpected path: {path}")

    try:
        run_smoke_check(failing_send)
    except SmokeCheckError as exc:
        assert exc.failure_class == "api_unavailable"
        assert "db offline" in exc.detail
    else:
        raise AssertionError("expected SmokeCheckError")


def test_live_smoke_reports_submission_failure_class() -> None:
    def failing_send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
        if path == "/":
            return 200, VALID_HTML, None, "text/html"
        if path == "/api/health":
            return 200, '{"service":"demo-launch-site-backend"}', {"service": "demo-launch-site-backend"}, "application/json"
        if path == "/api/contact-intakes":
            return 500, '{"detail":"write failed"}', {"detail": "write failed"}, "application/json"
        raise AssertionError(f"unexpected path: {path}")

    try:
        run_smoke_check(failing_send)
    except SmokeCheckError as exc:
        assert exc.failure_class == "submission_failed"
        assert "write failed" in exc.detail
    else:
        raise AssertionError("expected SmokeCheckError")


def test_live_smoke_accepts_semantically_valid_metadata_with_different_attribute_order() -> None:
    def flexible_send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
        if path == "/":
            html = """
            <!doctype html>
            <html>
              <head>
                <meta content="#111827" name="theme-color" />
                <meta content="https://demo-web-delivery.zeabur.app/" property="og:url" />
                <meta content="Demo Launch Site" property="og:title" />
                <link href="https://demo-web-delivery.zeabur.app/" rel="canonical" />
                <meta content="summary" name="twitter:card" />
                <meta content="https://demo-web-delivery.zeabur.app/og-image.svg" property="og:image" />
                <meta content="Demo Launch Site" name="twitter:title" />
                <meta content="https://demo-web-delivery.zeabur.app/og-image.svg" name="twitter:image" />
                <title>Demo Launch Site</title>
              </head>
              <body></body>
            </html>
            """
            return 200, html, None, "text/html"
        if path == "/api/health":
            return 200, '{"service":"demo-launch-site-backend"}', {"service": "demo-launch-site-backend"}, "application/json"
        if path == "/api/contact-intakes" and method == "POST":
            return 201, '{"message":"ok"}', {"message": "ok"}, "application/json"
        if path == "/api/contact-intakes" and method == "GET":
            return 200, '[{"email":"smoke-test@example.com"}]', [{"email": "smoke-test@example.com"}], "application/json"
        raise AssertionError(f"unexpected {method} path: {path}")

    report = run_smoke_check(flexible_send)

    assert report["metadata_checks"]["canonical_ok"] is True
    assert report["metadata_checks"]["og_title_ok"] is True
    assert report["metadata_checks"]["twitter_title_ok"] is True


def test_live_smoke_reports_metadata_failure_class() -> None:
    def failing_send(method: str, path: str, payload: dict | None = None) -> tuple[int, str, dict | None, str | None]:
        if path == "/":
            html = """
            <!doctype html>
            <html>
              <head>
                <title>Wrong Title</title>
              </head>
              <body></body>
            </html>
            """
            return 200, html, None, "text/html"
        if path == "/api/health":
            return 200, '{"service":"demo-launch-site-backend"}', {"service": "demo-launch-site-backend"}, "application/json"
        raise AssertionError(f"unexpected path: {path}")

    try:
        run_smoke_check(failing_send)
    except SmokeCheckError as exc:
        assert exc.failure_class == "metadata_invalid"
        assert "title_ok" in exc.detail
    else:
        raise AssertionError("expected SmokeCheckError")


def test_live_smoke_cli_runs_against_local_server() -> None:
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "web.backend.deploy_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8091",
        ],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(30):
            try:
                with urlopen("http://127.0.0.1:8091/api/health", timeout=1):
                    break
            except Exception:
                time.sleep(0.5)
        else:
            raise AssertionError("local uvicorn server did not become ready")

        result = subprocess.run(
            [sys.executable, "scripts/live_smoke_check.py", "http://127.0.0.1:8091"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        assert '"submit_status": 201' in result.stdout
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_live_smoke_cli_returns_failure_class_for_broken_frontend() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/live_smoke_check.py", "https://demo-web-delivery.zeabur.app/definitely-missing-base"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert '"failure_class": "metadata_invalid"' in result.stderr


def test_live_smoke_cli_returns_frontend_unavailable_for_connection_refused() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/live_smoke_check.py", "http://127.0.0.1:65500"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert '"failure_class": "frontend_unavailable"' in result.stderr
