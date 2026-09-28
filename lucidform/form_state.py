"""Form state. No public setter. `commit` is the single write path (Algorithm 1) and re-verifies
everything itself — nothing is assumed established by an earlier stage."""
from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from . import events
from .confirmation import ConfirmationReceipt
from .fingerprint import fingerprint
from .normalize import normalize
from .spec import FormSpec
from .types import Candidate, Status


class SilentWriteBlocked(PermissionError):
    pass


class FormState:
    __slots__ = ("_form", "_values")

    def __init__(self, form: FormSpec):
        self._form = form
        self._values: dict[str, str] = {}

    @property
    def form(self) -> FormSpec:
        return self._form

    def confirmed(self) -> Mapping[str, str]:
        return MappingProxyType(dict(self._values))

    def is_confirmed(self, field_id: str) -> bool:
        return field_id in self._values

    def pending(self) -> list[str]:
        return [f for f in self._form.ids if f not in self._values]

    def commit(self, field_id: str, candidate: Candidate, receipt: ConfirmationReceipt) -> str:
        try:
            assert isinstance(receipt, ConfirmationReceipt), "not a receipt"
            assert isinstance(candidate, Candidate), "not a candidate"
            assert receipt.field_id == field_id == candidate.field_id, "field mismatch"
            assert receipt.candidate_id == candidate.candidate_id, "candidate mismatch"
            assert receipt.validation.status is Status.PASS, "validation did not pass"
            assert receipt.validation.candidate_id == candidate.candidate_id, "report is for another candidate"
            assert receipt.affirmation.explicit is True, "affirmation not explicit"
            spec = self._form.get(field_id)
            value = normalize(candidate.value, spec, self._form.extra(field_id, "aliases"))
            assert value, "empty value"
            assert value == receipt.validation.normalized_value, "value differs from validated value"
            assert receipt.candidate_fingerprint == fingerprint(field_id, value, candidate.candidate_id), \
                "fingerprint mismatch"
        except (AssertionError, StopIteration, AttributeError) as e:
            events.emit("SILENT_WRITE_BLOCKED", field_id=field_id, candidate=candidate, why=str(e))
            raise SilentWriteBlocked(f"{field_id}: {e}") from None
        self._values[field_id] = value  # the ONLY write to _values
        events.emit("COMMIT", field_id=field_id, candidate=candidate, receipt=receipt)
        return value
