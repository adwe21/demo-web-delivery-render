from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from web.backend.smoke import SmokeCheckError, build_url_sender, run_smoke_check


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live smoke checks for the deployed demo site.")
    parser.add_argument("base_url", help="Public base URL, e.g. https://demo-web-delivery.zeabur.app")
    args = parser.parse_args()

    try:
        report = run_smoke_check(build_url_sender(args.base_url))
    except SmokeCheckError as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "failure_class": exc.failure_class,
                    "detail": exc.detail,
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
