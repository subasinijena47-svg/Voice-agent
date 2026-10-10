"""Data structures for the Home Credit LAP qualification prototype."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class QualificationState:
    """Conversation state. Eligibility fields are kept separate from call phase."""

    phase: str = "verify"
    customer_verified: bool = False
    callback_time: str | None = None

    property_type: str | None = None
    ownership_status: str | None = None
    documents_available: bool | None = None
    loan_amount_rupees: int | None = None
    requested_loan_amount_rupees: int | None = None
    occupation: str | None = None
    income_mode: str | None = None
    market_value_rupees: int | None = None
    market_value_note: str | None = None
    market_value_answered: bool = False
    tenure_years: int | None = None

    pending_cap_confirmation: bool = False
    transfer_required: bool = False
    disqualified: bool = False
    disqualification_reason: str | None = None
    result: str | None = None
    call_ended: bool = False
    last_question_group: str | None = None

    def next_missing_group(self) -> str | None:
        """Return the earliest unanswered checklist group in the required order."""
        checks = [
            ("property_type", self.property_type is not None),
            ("ownership_status", self.ownership_status is not None),
            ("documents_available", self.documents_available is not None),
            ("loan_amount", self.loan_amount_rupees is not None),
            (
                "occupation_income",
                self.occupation is not None and self.income_mode is not None,
            ),
            ("market_value", self.market_value_answered),
            ("tenure", self.tenure_years is not None),
        ]
        for group, complete in checks:
            if not complete:
                return group
        return None

    def checklist_complete(self) -> bool:
        return self.next_missing_group() is None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
