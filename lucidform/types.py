"""Core value types shared across stages. All frozen: nothing downstream may mutate a proposal."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Reason(str, Enum):
    """Closed, ordered rejection taxonomy (paper Table I). Order == check order."""
    EMPTY = "EMPTY"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    FORMAT = "FORMAT"
    ENUM = "ENUM"
    CHECKSUM = "CHECKSUM"
    RANGE = "RANGE"
    CROSS_FIELD = "CROSS_FIELD"
    AMBIGUOUS_EXTRACTION = "AMBIGUOUS_EXTRACTION"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


CHECK_ORDER: tuple[Reason, ...] = tuple(Reason)


class Status(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"


class Intent(str, Enum):
    VALUE = "value"            # user stated a value
    QUESTION = "question"      # user asked what the field means / where to find it
    DECLINE = "decline"        # user refuses / skips
    UNRECOVERABLE = "unrecoverable"


@dataclass(frozen=True)
class FieldSpec:
    field_id: str
    kind: str                          # name|date|enum|pan|aadhaar|pincode|mobile|email|text|city
    prompt: str = ""
    gloss: str = ""
    max_length: int | None = None
    exact_length: int | None = None    # length after normalization, for fixed-width ids
    pattern: str | None = None
    options: tuple[str, ...] = ()
    required: bool = True
    readback: str = "plain"            # plain|chars|digits|date
    cross: tuple[dict, ...] = ()       # cross-field rules from overlay
    prompt_hi: str = ""
    gloss_hi: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Candidate:
    """A proposal from extraction. Never a value the system holds as fact."""
    field_id: str
    value: str
    intent: Intent = Intent.VALUE
    quote: str = ""
    confidence: float = 1.0
    ambiguous: bool = False
    alternatives: tuple[str, ...] = ()
    grounded: bool = True
    candidate_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["intent"] = self.intent.value
        return d


@dataclass(frozen=True)
class ValidationReport:
    field_id: str
    candidate_id: str
    status: Status
    reason: Reason | None = None
    detail: str = ""
    normalized_value: str | None = None

    @property
    def passed(self) -> bool:
        return self.status is Status.PASS

    def to_dict(self) -> dict[str, Any]:
        return {"field_id": self.field_id, "candidate_id": self.candidate_id, "status": self.status.value,
                "reason": self.reason.value if self.reason else None, "detail": self.detail,
                "normalized_value": self.normalized_value}


@dataclass(frozen=True)
class Affirmation:
    explicit: bool
    basis: str
    utterance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
