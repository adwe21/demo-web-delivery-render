from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SUCCESS_SIGNALS = ["root_status", "health_status", "submit_status", "list_status"]


def _escape_cell(value: object) -> str:
    text = str(value)
    text = text.replace("`", "'")
    text = text.replace("|", "\\|")
    text = text.replace("\n", " ")
    return text


def _invalid_payload(detail: str) -> dict[str, str]:
    return {
        "failure_class": "summary_payload_invalid",
        "detail": detail,
    }


def _load_payload(path: Path) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, {
            "failure_class": "summary_payload_missing",
            "detail": f"failed to read {path.name}: {exc}",
        }

    try:
        decoded = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return None, _invalid_payload(f"failed to parse {path.name}: {exc}")

    if not isinstance(decoded, dict):
        return None, _invalid_payload(f"expected JSON object in {path.name}, got {type(decoded).__name__}")

    return decoded, None


def _bool_icon(value: object) -> str:
    return "✅" if bool(value) else "❌"


def _code(value: object) -> str:
    return f"`{_escape_cell(value)}`"


def render_success(payload: dict[str, Any]) -> str:
    lines = [
        "## smoke success signal",
        "",
        "### request path checks",
        "| Signal | Status |",
        "| --- | --- |",
    ]
    for signal in SUCCESS_SIGNALS:
        lines.append(f"| {_escape_cell(signal)} | {_code(payload.get(signal, 'missing'))} |")

    metadata_checks = payload.get("metadata_checks", {}) or {}
    if not isinstance(metadata_checks, dict):
        metadata_checks = {"metadata_checks_shape": False}
    lines.extend([
        "",
        "### metadata checks",
        "| Check | Result |",
        "| --- | --- |",
    ])
    for check, result in metadata_checks.items():
        lines.append(f"| {_escape_cell(check)} | {_bool_icon(result)} |")

    return "\n".join(lines)


def render_failure(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## smoke failure signal",
            "",
            "### failure summary",
            "| Field | Value |",
            "| --- | --- |",
            f"| failure_class | {_code(payload.get('failure_class', 'unknown'))} |",
            f"| detail | {_code(payload.get('detail', 'missing detail'))} |",
        ]
    )


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: write_smoke_summary.py <success|failure> <payload_path>", file=sys.stderr)
        return 2

    mode = argv[1]
    if mode not in {"success", "failure"}:
        print(f"unsupported mode: {mode}", file=sys.stderr)
        return 2

    payload_path = Path(argv[2])
    payload, load_error = _load_payload(payload_path)

    if load_error is not None:
        print(render_failure(load_error))
        return 0

    if mode == "success":
        print(render_success(payload or {}))
        return 0

    print(render_failure(payload or {}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
