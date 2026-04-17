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
  - homepage metadata contract:
    - `title`
    - `canonical`
    - `theme-color`
    - `og:*`
    - `twitter:*`
- Failure signals are classified as:
  - `frontend_unavailable`
  - `metadata_invalid`
  - `api_unavailable`
  - `submission_failed`
  - `list_verification_failed`
