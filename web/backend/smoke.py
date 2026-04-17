from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4
import json


SendFn = Callable[[str, str, dict[str, Any] | None], tuple[int, str, dict[str, Any] | list[Any] | None, str | None]]


@dataclass
class SmokeCheckError(RuntimeError):
    failure_class: str
    detail: str

    def __str__(self) -> str:
        return f"{self.failure_class}: {self.detail}"


@dataclass(frozen=True)
class SmokeReport:
    root_status: int
    health_status: int
    submit_status: int
    list_status: int
    service: str
    submitted_email: str
    listed_emails: list[str]
    metadata_checks: dict[str, bool]

    def as_dict(self) -> dict[str, Any]:
        return {
            "root_status": self.root_status,
            "health_status": self.health_status,
            "submit_status": self.submit_status,
            "list_status": self.list_status,
            "service": self.service,
            "submitted_email": self.submitted_email,
            "listed_emails": self.listed_emails,
            "metadata_checks": self.metadata_checks,
        }


class _MetadataHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = {key.lower(): (value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "link":
            self.links.append(normalized)
        elif tag == "meta":
            self.metas.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def _metadata_checks_from_html(html: str) -> dict[str, bool]:
    parser = _MetadataHTMLParser()
    parser.feed(html)

    def has_link(rel: str, href: str) -> bool:
        return any(
            rel in {item.strip().lower() for item in link.get("rel", "").split()}
            and link.get("href", "") == href
            for link in parser.links
        )

    def has_meta(attr_name: str, attr_value: str, content: str) -> bool:
        return any(meta.get(attr_name, "") == attr_value and meta.get("content", "") == content for meta in parser.metas)

    return {
        "title_ok": parser.title == "Demo Launch Site",
        "canonical_ok": has_link("canonical", "https://demo-web-delivery.zeabur.app/"),
        "theme_color_ok": has_meta("name", "theme-color", "#111827"),
        "og_title_ok": has_meta("property", "og:title", "Demo Launch Site"),
        "og_url_ok": has_meta("property", "og:url", "https://demo-web-delivery.zeabur.app/"),
        "og_image_ok": has_meta("property", "og:image", "https://demo-web-delivery.zeabur.app/og-image.png"),
        "og_image_alt_ok": has_meta(
            "property",
            "og:image:alt",
            "Demo Launch Site social preview card showing proof-ready launch narrative and delivery chain.",
        ),
        "twitter_card_ok": has_meta("name", "twitter:card", "summary_large_image"),
        "twitter_title_ok": has_meta("name", "twitter:title", "Demo Launch Site"),
        "twitter_image_ok": has_meta("name", "twitter:image", "https://demo-web-delivery.zeabur.app/og-image.png"),
        "twitter_image_alt_ok": has_meta(
            "name",
            "twitter:image:alt",
            "Demo Launch Site social preview card showing proof-ready launch narrative and delivery chain.",
        ),
    }


def run_smoke_check(send: SendFn) -> dict[str, Any]:
    suffix = uuid4().hex[:8]
    payload = {
        "name": f"Smoke Runner {suffix}",
        "email": f"smoke-{suffix}@example.com",
        "company": "Hermes QA",
        "use_case": "Automated smoke verification for root page, health endpoint, contact submission flow, and metadata contract.",
        "source": "launch-page",
    }

    root_status, root_text, _, root_content_type = send("GET", "/", None)
    if root_status != 200:
        raise SmokeCheckError("frontend_unavailable", f"root check failed: {root_status} {root_text[:200]}")
    if root_content_type is not None and "text/html" not in root_content_type:
        raise SmokeCheckError("frontend_unavailable", f"root content-type mismatch: {root_content_type}")

    metadata_checks = _metadata_checks_from_html(root_text)
    failed_metadata = [name for name, ok in metadata_checks.items() if not ok]
    if failed_metadata:
        raise SmokeCheckError("metadata_invalid", f"metadata checks failed: {', '.join(failed_metadata)}")

    health_status, health_text, health_json, _ = send("GET", "/api/health", None)
    if health_status != 200 or not isinstance(health_json, dict):
        raise SmokeCheckError("api_unavailable", f"health check failed: {health_status} {health_text[:200]}")

    submit_status, submit_text, submit_json, _ = send("POST", "/api/contact-intakes", payload)
    if submit_status != 201 or not isinstance(submit_json, dict):
        raise SmokeCheckError("submission_failed", f"submit failed: {submit_status} {submit_text[:200]}")

    list_status, list_text, list_json, _ = send("GET", "/api/contact-intakes", None)
    if list_status != 200 or not isinstance(list_json, list):
        raise SmokeCheckError("list_verification_failed", f"list failed: {list_status} {list_text[:200]}")

    listed_emails = [item.get("email", "") for item in list_json if isinstance(item, dict)]
    report = SmokeReport(
        root_status=root_status,
        health_status=health_status,
        submit_status=submit_status,
        list_status=list_status,
        service=str(health_json.get("service", "")),
        submitted_email=payload["email"],
        listed_emails=listed_emails,
        metadata_checks=metadata_checks,
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
        except URLError as exc:
            raise SmokeCheckError("frontend_unavailable", f"request failed for {path}: {exc.reason}") from exc

    return send
