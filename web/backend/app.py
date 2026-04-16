from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

APP_NAME = "demo-launch-site-backend"
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_FILE = DATA_DIR / "contact_intakes.json"


class ContactIntakeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=160)
    company: str = Field(min_length=2, max_length=120)
    use_case: str = Field(min_length=10, max_length=1200)
    source: Literal["launch-page", "sales-demo", "partner-referral"] = "launch-page"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("must be a valid work email")
        return normalized


class ContactIntakeRecord(ContactIntakeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: str
    status: Literal["received"] = "received"


class ContactIntakeResponse(BaseModel):
    intake: ContactIntakeRecord
    message: str
    next_step: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    utc_time: str
    intakes_count: int


class ContractSummary(BaseModel):
    service: str
    healthcheck: str
    submit_intake: str
    list_intakes: str
    request_example: ContactIntakeCreate


class IntakeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def _read(self) -> list[dict]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def list(self) -> list[ContactIntakeRecord]:
        with self._lock:
            return [ContactIntakeRecord.model_validate(item) for item in self._read()]

    def create(self, payload: ContactIntakeCreate) -> ContactIntakeRecord:
        record = ContactIntakeRecord(
            id=f"intake_{uuid4().hex[:12]}",
            created_at=datetime.now(timezone.utc).isoformat(),
            **payload.model_dump(),
        )
        with self._lock:
            current = self._read()
            current.append(record.model_dump())
            self.path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record


store = IntakeStore(DATA_FILE)
app = FastAPI(
    title="Demo Launch Site Backend",
    version="0.1.0",
    description="Backend skeleton for the Demo Launch Site contact intake flow.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def healthcheck() -> HealthResponse:
    return HealthResponse(
        service=APP_NAME,
        utc_time=datetime.now(timezone.utc).isoformat(),
        intakes_count=len(store.list()),
    )


@app.get("/api/contact-intakes", response_model=list[ContactIntakeRecord], tags=["contact-intakes"])
def list_contact_intakes() -> list[ContactIntakeRecord]:
    return store.list()


@app.post("/api/contact-intakes", response_model=ContactIntakeResponse, status_code=201, tags=["contact-intakes"])
def create_contact_intake(payload: ContactIntakeCreate) -> ContactIntakeResponse:
    record = store.create(payload)
    return ContactIntakeResponse(
        intake=record,
        message="Launch intake captured.",
        next_step="Sales or product can review the intake payload and follow up.",
    )


@app.get("/api/contact-intakes/contract", response_model=ContractSummary, tags=["contact-intakes"])
def get_contract_summary() -> ContractSummary:
    return ContractSummary(
        service=APP_NAME,
        healthcheck="GET /api/health",
        submit_intake="POST /api/contact-intakes",
        list_intakes="GET /api/contact-intakes",
        request_example=ContactIntakeCreate(
            name="Alex Chen",
            email="alex@company.com",
            company="Northstar Labs",
            use_case="We need a launch page for partner demos, waitlist capture, and investor meetings next month.",
            source="launch-page",
        ),
    )
