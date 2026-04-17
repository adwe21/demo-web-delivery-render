from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-smoke.yml"


def test_ci_workflow_runs_backend_and_frontend_validation() -> None:
    assert WORKFLOW.exists(), "push validation workflow should exist for automatic acceptance"

    content = WORKFLOW.read_text()

    assert "on:" in content
    assert "push:" in content
    assert "main" in content
    assert "pip install -r requirements.txt pytest httpx" in content
    assert "python -m pytest -q tests/web/test_demo_launch_backend.py tests/web/test_demo_launch_frontend_integration.py tests/web/test_demo_launch_deploy.py tests/web/test_deploy_container_contract.py tests/web/test_live_smoke.py" in content
    assert "node-version: '20'" in content
    assert "npm run build" in content
    assert "python -m uvicorn web.backend.deploy_app:app --host 127.0.0.1 --port 8080" in content
    assert "python scripts/live_smoke_check.py http://127.0.0.1:8080" in content
    assert "urllib.request.urlopen(\"http://127.0.0.1:8080/api/health\"" in content
