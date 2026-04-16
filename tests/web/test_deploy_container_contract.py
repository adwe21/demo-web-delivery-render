from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = REPO_ROOT / "Dockerfile"


def test_deploy_container_builds_frontend_and_runs_uvicorn() -> None:
    assert DOCKERFILE.exists(), "repo-root Dockerfile is required for Zeabur build stability"

    content = DOCKERFILE.read_text()

    assert "FROM node:20-alpine" in content
    assert "npm install" in content
    assert "npm run build" in content
    assert "COPY --from=frontend-builder /app/web/dist ./web/dist" in content
    assert "COPY web/backend ./web/backend" in content
    assert "COPY web/backend/data ./web/backend/data" in content
    assert "RUN pip install --no-cache-dir -r requirements.txt" in content
    assert "CMD [\"python\", \"-m\", \"uvicorn\", \"web.backend.deploy_app:app\"" in content
