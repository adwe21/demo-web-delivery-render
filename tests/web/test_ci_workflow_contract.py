from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-smoke.yml"
SUMMARY_SCRIPT = REPO_ROOT / "scripts" / "write_smoke_summary.py"


def test_ci_workflow_runs_backend_and_frontend_validation() -> None:
    assert WORKFLOW.exists(), "push validation workflow should exist for automatic acceptance"
    assert SUMMARY_SCRIPT.exists(), "workflow should use a checked-in smoke summary formatter"

    content = WORKFLOW.read_text()
    summary_script = SUMMARY_SCRIPT.read_text()

    assert "on:" in content
    assert "push:" in content
    assert "main" in content
    assert "pip install -r requirements.txt pytest httpx" in content
    assert "python -m pytest -q tests/web/test_demo_launch_backend.py tests/web/test_demo_launch_frontend_integration.py tests/web/test_demo_launch_deploy.py tests/web/test_deploy_container_contract.py tests/web/test_live_smoke.py tests/web/test_smoke_summary_script.py" in content
    assert "node-version: '20'" in content
    assert "npm run build" in content
    assert "python -m uvicorn web.backend.deploy_app:app --host 127.0.0.1 --port 8080" in content
    assert "python scripts/live_smoke_check.py http://127.0.0.1:8080 >smoke-report.json 2>smoke-error.log" in content
    assert "python scripts/write_smoke_summary.py success smoke-report.json >> \"$GITHUB_STEP_SUMMARY\"" in content
    assert "python scripts/write_smoke_summary.py failure smoke-error.log >> \"$GITHUB_STEP_SUMMARY\"" in content
    assert "urllib.request.urlopen(\"http://127.0.0.1:8080/api/health\"" in content

    assert "## smoke success signal" in summary_script
    assert "## smoke failure signal" in summary_script
    assert "### request path checks" in summary_script
    assert "### metadata checks" in summary_script
    assert "| Check | Result |" in summary_script
    assert "| Signal | Status |" in summary_script
