from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "web" / "src" / "App.tsx"
API_PATH = ROOT / "web" / "src" / "lib" / "api.ts"
HTML_PATH = ROOT / "web" / "index.html"
FAVICON_PATH = ROOT / "web" / "public" / "favicon.svg"


def test_frontend_submit_handler_calls_backend_api() -> None:
    app_source = APP_PATH.read_text(encoding="utf-8")

    assert 'api.submitContactIntake({' in app_source
    assert 'use_case: form.useCase' in app_source
    assert 'setSubmitState("success")' in app_source
    assert 'setSubmitState("error")' in app_source


def test_frontend_api_helper_targets_contact_intakes_endpoint() -> None:
    api_source = API_PATH.read_text(encoding="utf-8")

    assert 'submitContactIntake: (payload: ContactIntakePayload)' in api_source
    assert 'fetchJSON<ContactIntakeSubmission>("/api/contact-intakes"' in api_source


def test_frontend_branding_uses_shared_site_name_and_page_metadata() -> None:
    app_source = APP_PATH.read_text(encoding="utf-8")
    html_source = HTML_PATH.read_text(encoding="utf-8")

    assert 'const SITE_NAME = "Demo Launch Site"' in app_source
    assert '{SITE_NAME}' in app_source
    assert '<title>Demo Launch Site</title>' in html_source
    assert 'name="description"' in html_source
    assert 'href="/favicon.svg"' in html_source


def test_frontend_has_custom_svg_favicon_asset() -> None:
    assert FAVICON_PATH.exists(), "expected a checked-in custom favicon asset for the launch site"

    favicon_source = FAVICON_PATH.read_text(encoding="utf-8")

    assert '<svg' in favicon_source
    assert 'Demo Launch Site' in favicon_source
