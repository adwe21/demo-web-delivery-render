from __future__ import annotations

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "web" / "src" / "App.tsx"
API_PATH = ROOT / "web" / "src" / "lib" / "api.ts"
HTML_PATH = ROOT / "web" / "index.html"
FAVICON_PATH = ROOT / "web" / "public" / "favicon.svg"
OG_IMAGE_PATH = ROOT / "web" / "public" / "og-image.svg"
OG_IMAGE_PNG_PATH = ROOT / "web" / "public" / "og-image.png"


def _read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        signature = fh.read(8)
        assert signature == b"\x89PNG\r\n\x1a\n"
        _length = fh.read(4)
        chunk_type = fh.read(4)
        assert chunk_type == b"IHDR"
        width, height = struct.unpack(">II", fh.read(8))
        return width, height


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
    assert 'rel="canonical" href="https://demo-web-delivery.zeabur.app/"' in html_source
    assert 'name="theme-color" content="#111827"' in html_source
    assert 'property="og:title" content="Demo Launch Site"' in html_source
    assert 'property="og:type" content="website"' in html_source
    assert 'property="og:url" content="https://demo-web-delivery.zeabur.app/"' in html_source
    assert 'property="og:image" content="https://demo-web-delivery.zeabur.app/og-image.png"' in html_source
    assert 'property="og:image:alt"' in html_source
    assert 'Demo Launch Site social preview card showing proof-ready launch narrative and delivery chain.' in html_source
    assert 'name="twitter:card" content="summary_large_image"' in html_source
    assert 'name="twitter:title" content="Demo Launch Site"' in html_source
    assert 'name="twitter:image" content="https://demo-web-delivery.zeabur.app/og-image.png"' in html_source
    assert 'name="twitter:image:alt"' in html_source
    assert 'Demo Launch Site social preview card showing proof-ready launch narrative and delivery chain.' in html_source


def test_frontend_has_custom_svg_favicon_asset() -> None:
    assert FAVICON_PATH.exists(), "expected a checked-in custom favicon asset for the launch site"

    favicon_source = FAVICON_PATH.read_text(encoding="utf-8")

    assert '<svg' in favicon_source
    assert 'Demo Launch Site' in favicon_source


def test_frontend_has_dedicated_og_image_asset() -> None:
    assert OG_IMAGE_PATH.exists(), "expected a checked-in dedicated OG image asset"
    assert OG_IMAGE_PNG_PATH.exists(), "expected a PNG fallback for social crawlers"

    og_source = OG_IMAGE_PATH.read_text(encoding="utf-8")

    assert '<svg' in og_source
    assert 'viewBox="0 0 1200 630"' in og_source
    assert 'Demo Launch Site' in og_source
    assert 'Proof-ready launch narrative' in og_source
    assert 'Live intake' in og_source
    assert 'CI-guarded deploys' in og_source
    assert 'Share-ready branding' in og_source
    assert '72h launch sprint' in og_source
    assert 'Launch credibility, not just a landing page.' in og_source
    assert 'demo-web-delivery.zeabur.app' in og_source

    assert OG_IMAGE_PNG_PATH.stat().st_size > 0
    assert _read_png_size(OG_IMAGE_PNG_PATH) == (1200, 630)
