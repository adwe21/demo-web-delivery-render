from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY_SCRIPT = REPO_ROOT / "scripts" / "write_smoke_summary.py"


def test_smoke_summary_script_formats_success_payload_as_grouped_tables(tmp_path: Path) -> None:
    payload_path = tmp_path / "smoke-report.json"
    payload_path.write_text(
        json.dumps(
            {
                "root_status": 200,
                "health_status": 200,
                "submit_status": 201,
                "list_status": 200,
                "metadata_checks": {
                    "title_ok": True,
                    "og_image_ok": True,
                    "twitter_image_ok": True,
                },
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "success", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## smoke success signal" in result.stdout
    assert "### request path checks" in result.stdout
    assert "| Signal | Status |" in result.stdout
    assert "| root_status | `200` |" in result.stdout
    assert "| submit_status | `201` |" in result.stdout
    assert "### metadata checks" in result.stdout
    assert "| Check | Result |" in result.stdout
    assert "| title_ok | ✅ |" in result.stdout
    assert "| twitter_image_ok | ✅ |" in result.stdout


def test_smoke_summary_script_formats_failure_payload_as_summary_table(tmp_path: Path) -> None:
    payload_path = tmp_path / "smoke-error.log"
    payload_path.write_text(
        json.dumps(
            {
                "failure_class": "metadata_invalid",
                "detail": "metadata checks failed: title_ok, og_image_ok",
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "failure", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## smoke failure signal" in result.stdout
    assert "### failure summary" in result.stdout
    assert "| Field | Value |" in result.stdout
    assert "| failure_class | `metadata_invalid` |" in result.stdout
    assert "| detail | `metadata checks failed: title_ok, og_image_ok` |" in result.stdout


def test_smoke_summary_script_falls_back_to_controlled_failure_summary_for_invalid_json(tmp_path: Path) -> None:
    payload_path = tmp_path / "smoke-error.log"
    payload_path.write_text("not-json", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "failure", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## smoke failure signal" in result.stdout
    assert "| failure_class | `summary_payload_invalid` |" in result.stdout
    assert "failed to parse" in result.stdout


def test_smoke_summary_script_falls_back_to_controlled_failure_summary_for_missing_file(tmp_path: Path) -> None:
    payload_path = tmp_path / "missing.json"

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "failure", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## smoke failure signal" in result.stdout
    assert "| failure_class | `summary_payload_missing` |" in result.stdout
    assert "failed to read" in result.stdout


def test_smoke_summary_script_rejects_valid_non_object_json_with_controlled_failure_summary(tmp_path: Path) -> None:
    payload_path = tmp_path / "smoke-error.log"
    payload_path.write_text("[]", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "failure", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## smoke failure signal" in result.stdout
    assert "| failure_class | `summary_payload_invalid` |" in result.stdout
    assert "expected JSON object" in result.stdout


def test_smoke_summary_script_rejects_unsupported_mode_before_reading_payload(tmp_path: Path) -> None:
    payload_path = tmp_path / "missing.json"

    result = subprocess.run(
        [sys.executable, str(SUMMARY_SCRIPT), "weird", str(payload_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "unsupported mode: weird" in result.stderr
