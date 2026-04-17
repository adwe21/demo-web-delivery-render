# Demo Web Delivery

Public deploy target for the Demo Launch Site.

## Smoke checks

- Local/live reusable smoke command:
  ```bash
  python scripts/live_smoke_check.py https://demo-web-delivery.zeabur.app
  ```
- Covers:
  - `/`
  - `/api/health`
  - `POST /api/contact-intakes`
  - `GET /api/contact-intakes`
- Failure signals are classified as:
  - `frontend_unavailable`
  - `api_unavailable`
  - `submission_failed`
  - `list_verification_failed`
