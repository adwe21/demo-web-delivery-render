from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from web.backend.app import app as app


WEB_DIST = Path(__file__).resolve().parents[1] / "dist"


def _safe_static_path(full_path: str) -> Path | None:
    if not full_path:
        return None
    candidate = (WEB_DIST / full_path).resolve()
    if not candidate.is_relative_to(WEB_DIST.resolve()):
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    return None


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    index = WEB_DIST / "index.html"
    if not index.exists():
        raise HTTPException(status_code=503, detail="frontend build not found")
    return FileResponse(index)


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend_asset(full_path: str) -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    static_file = _safe_static_path(full_path)
    if static_file is not None:
        return FileResponse(static_file)
    index = WEB_DIST / "index.html"
    if not index.exists():
        raise HTTPException(status_code=503, detail="frontend build not found")
    return FileResponse(index)
