from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4
import json


SendFn = Callable[[str, str, dict[str, Any] | None], tuple[int, str, dict[str, Any] | list[Any] | None, str | None]]


@dataclass(frozen=True)
class SmokeReport:
    root_status: int
    health_status: int
    submit_status: int
    list_status: int
    service: str
    submitted_email: str
    listed_emails: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "root_status": self.root_status,
            "health_status": self.health_status,
            "submit_status": self.submit_status,
            "list_status": self.list_status,
            "service": self.service,
            "submitted_email": self.submitted_email,
            "listed_emails": self.listed_emails,
        }


def run_smoke_check(send: SendFn) -> dict[str, Any]:
    suffix = uuid4().hex[:8]
    payload = {
        "name": f"Smoke Runner {suffix}",
        "email": f"smoke-{suffix}@example.com",
        "company": "Hermes QA",
        "use_case": "Automated smoke verification for root page, health endpoint, and contact submission flow.",
        "source": "launch-page",
    }

    root_status, root_text, _, root_content_type = send("GET", "/", None)
    if root_status != 200:
        raise RuntimeError(f"root check failed: {root_status} {root_text[:200]}")
    if root_content_type is not None and "text/html" not in root_content_type:
        raise RuntimeError(f"root content-type mismatch: {root_content_type}")

    health_status, health_text, health_json, _ = send("GET", "/api/health", None)
    if health_status != 200 or not isinstance(health_json, dict):
        raise RuntimeError(f"health check failed: {health_status} {health_text[:200]}")

    submit_status, submit_text, submit_json, _ = send("POST", "/api/contact-intakes", payload)
    if submit_status != 201 or not isinstance(submit_json, dict):
        raise RuntimeError(f"submit failed: {submit_status} {submit_text[:200]}")

    list_status, list_text, list_json, _ = send("GET", "/api/contact-intakes", None)
    if list_status != 200 or not isinstance(list_json, list):
        raise RuntimeError(f"list failed: {list_status} {list_text[:200]}")

    listed_emails = [item.get("email", "") for item in list_json if isinstance(item, dict)]
    report = SmokeReport(
        root_status=root_status,
        health_status=health_status,
        submit_status=submit_status,
        list_status=list_status,
        service=str(health_json.get("service", "")),
        submitted_email=payload["email"],
        listed_emails=listed_emails,
    )
    return report.as_dict()


def build_url_sender(base_url: str, timeout: int = 15) -> SendFn:
    normalized = base_url.rstrip("/")

    def send(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, str, dict[str, Any] | list[Any] | None, str | None]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{normalized}{path}",
            data=data,
            headers={"Content-Type": "application/json"} if payload is not None else {},
            method=method,
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                content_type = response.headers.get("Content-Type")
                try:
                    parsed: dict[str, Any] | list[Any] | None = json.loads(body)
                except json.JSONDecodeError:
                    parsed = None
                return response.status, body, parsed, content_type
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            return exc.code, body, parsed, exc.headers.get("Content-Type")

    return send
