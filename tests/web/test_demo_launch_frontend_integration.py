from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "web" / "src" / "App.tsx"
API_PATH = ROOT / "web" / "src" / "lib" / "api.ts"


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
