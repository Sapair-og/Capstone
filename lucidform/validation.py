"""The validation gate (paper §III-B, Algorithm 2).

Deterministic. Imports no language-model client, directly or transitively — enforced by
tests/test_architecture.py, not by convention. Checks run in a fixed order; the first failure
is the reported reason, so a value is always reported by its most severe defect.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Callable, Mapping

from . import events
from .checksums import verhoeff_valid
from .normalize import base, normalize
from .rules_data import states_for_pincode
from .spec import FormSpec
from .types import CHECK_ORDER, Candidate, FieldSpec, Reason, Status, ValidationReport

_DEFAULT_PATTERN = {
    "name": r"^[A-Za-z][A-Za-z .'\-]*$",
    "city": r"^[A-Za-z][A-Za-z .\-]*$",
    "date": r"^[0-9]{2}/[0-9]{2}/[0-9]{4}$",
    "text": r"^[\x20-\x7e]+$",
}


class _Ctx:
    def __init__(self, cand: Candidate, spec: FieldSpec, form: FormSpec, confirmed: Mapping[str, str],
                 today: dt.date):
        self.cand, self.spec, self.form, self.confirmed, self.today = cand, spec, form, confirmed, today
        self.raw = base(cand.value)
        self.v = normalize(cand.value, spec, form.extra(spec.field_id, "aliases"))

    def extra(self, key, default=None):
        return self.form.extra(self.spec.field_id, key, default)


# Each check returns None (ok) or a human-readable detail string (fail).
def _empty(c: _Ctx):
    return "no value was given" if not c.v else None


def _type(c: _Ctx):
    s, n = c.spec, len(c.v)
    if s.exact_length and n != s.exact_length:
        return f"expected {s.exact_length} characters, got {n}"
    if s.max_length and n > s.max_length:
        return f"longer than the {s.max_length} characters this field allows"
    return None


def _format(c: _Ctx):
    if c.spec.kind == "enum":
        return None
    pat = c.spec.pattern or _DEFAULT_PATTERN.get(c.spec.kind)
    return None if pat is None or re.fullmatch(pat, c.v) else "does not have the shape this field needs"


def _enum(c: _Ctx):
    o = c.spec.options
    return None if not o or c.v in o else "is not one of the allowed options"


def _checksum(c: _Ctx):
    if c.extra("checksum") == "verhoeff" and not verhoeff_valid(c.v):
        return "the check digit does not match — one digit is likely wrong"
    return None


def _range(c: _Ctx):
    if c.spec.kind != "date":
        return None
    d, m, y = map(int, c.v.split("/"))
    try:
        born = dt.date(y, m, d)
    except ValueError:
        return "is not a real calendar date"
    if born > c.today:
        return "is in the future"
    age = c.today.year - born.year - ((c.today.month, c.today.day) < (born.month, born.day))
    if age < (lo := c.extra("min_age", 0)):
        return f"applicant must be at least {lo}"
    if age > (hi := c.extra("max_age", 150)):
        return f"age over {hi} is not plausible"
    return None


def _surname_initial(name: str) -> str:
    toks = base(name).split()
    return toks[-1][0].upper() if toks else ""


def _pan_vs_name(pan: str, name: str):
    return None if pan[4] == _surname_initial(name) else "PAN's fifth letter does not match your surname's first letter"


def _pin_vs_state(pin: str, state: str):
    ok = states_for_pincode(pin)
    return None if not ok or state in ok else f"PIN code {pin[:2]}xxxx is not in {state}"


_CROSS: dict[str, Callable[[str, str], str | None]] = {
    "pan_surname": _pan_vs_name,
    "surname_pan": lambda name, pan: _pan_vs_name(pan, name),
    "pincode_state": _pin_vs_state,
    "state_pincode": lambda state, pin: _pin_vs_state(pin, state),
}


def _cross(c: _Ctx):
    for rule in c.spec.cross:
        other = rule["with"]
        if other in c.confirmed:  # only confirmed values may influence the gate
            if detail := _CROSS[rule["rule"]](c.v, c.confirmed[other]):
                return detail
    return None


def _ambiguous(c: _Ctx):
    if not c.cand.grounded:
        return "the value could not be found in what you said"
    return "more than one reading was possible" if c.cand.ambiguous else None


def _confidence(c: _Ctx):
    return "the value was not heard clearly" if c.cand.confidence < c.form.confidence_threshold else None


_CHECKS: dict[Reason, Callable[[_Ctx], str | None]] = {
    Reason.EMPTY: _empty, Reason.TYPE_MISMATCH: _type, Reason.FORMAT: _format, Reason.ENUM: _enum,
    Reason.CHECKSUM: _checksum, Reason.RANGE: _range, Reason.CROSS_FIELD: _cross,
    Reason.AMBIGUOUS_EXTRACTION: _ambiguous, Reason.LOW_CONFIDENCE: _confidence,
}
assert tuple(_CHECKS) == CHECK_ORDER


def validate(cand: Candidate, form: FormSpec, confirmed: Mapping[str, str] | None = None,
             today: dt.date | None = None) -> ValidationReport:
    spec = form.get(cand.field_id)
    c = _Ctx(cand, spec, form, dict(confirmed or {}), today or dt.date.today())
    for reason in CHECK_ORDER:
        if (detail := _CHECKS[reason](c)) is not None:
            rep = ValidationReport(cand.field_id, cand.candidate_id, Status.REJECT, reason, detail)
            break
    else:
        rep = ValidationReport(cand.field_id, cand.candidate_id, Status.PASS, normalized_value=c.v)
    events.emit("VALIDATION", report=rep, candidate=cand)
    return rep
