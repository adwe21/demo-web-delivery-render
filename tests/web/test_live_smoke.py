from __future__ import annotations

from fastapi.testclient import TestClient
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from web.backend.deploy_app import app
from web.backend.smoke import run_smoke_check


client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[2]


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
