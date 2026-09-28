"""Confirmation parser (Algorithm 3) and the only place a ConfirmationReceipt can be born.

The parser is a whitelist over the WHOLE utterance, not a search for an affirmative token:
"yes, I know that's wrong" and "yesterday I gave the wrong number" must not confirm.
Negation/hedge cues are checked first; acknowledgements ("okay", "acha") are deliberately
not agreement. A false negative costs a re-ask; a false positive writes into a legal document.
"""
from __future__ import annotations

import sys
import unicodedata
from dataclasses import dataclass

from . import events
from .fingerprint import fingerprint
from .types import Affirmation, Candidate, ValidationReport

AFFIRMATION_WHITELIST = frozenset({
    "yes", "yes yes", "yes correct", "yes it is correct", "yes that is correct", "yes thats correct",
    "yes right", "yes thats right", "yes that is right", "yes confirm", "yes it is", "yes that is it",
    "correct", "that is correct", "thats correct", "its correct", "it is correct", "right", "thats right",
    "that is right", "confirm", "confirmed", "i confirm", "yep", "yeah", "yeah correct", "yes please",
    "haan", "haan ji", "han", "haan haan", "ji haan", "haan sahi hai", "sahi hai", "bilkul",
    "bilkul sahi", "haan bilkul", "theek hai sahi hai", "सही है", "हाँ", "हां", "हाँ जी", "जी हाँ", "हाँ सही है", "बिल्कुल",
})

# Any of these tokens anywhere defeats confirmation before the whitelist is consulted.
NEGATION_CUES = frozenset({
    "no", "not", "nope", "wrong", "incorrect", "dont", "isnt", "wasnt", "never", "nahi", "nahin", "na",
    "galat", "mat", "change", "wait", "ruko", "except", "but", "mistake", "नहीं", "गलत", "ना",
})
HEDGE_CUES = frozenset({
    "maybe", "perhaps", "probably", "think", "guess", "unsure", "sure", "shayad", "lagta", "possibly",
    "might", "suppose", "शायद",
})
FILLER = frozenset({"um", "umm", "uh", "uhh", "er", "hmm", "well", "so", "oh", "arre", "accha ji"})


def _tokens(utterance: str) -> list[str]:
    s = utterance.casefold().replace("'", "").replace("’", "")
    s = "".join(" " if unicodedata.category(ch)[0] in "PS" else ch for ch in s)  # keeps Devanagari marks
    return [t for t in s.split() if t not in FILLER]


def parse_affirmation(utterance: str) -> Affirmation:
    toks = _tokens(utterance or "")
    if any(t in NEGATION_CUES for t in toks) or any(t in HEDGE_CUES for t in toks):
        return Affirmation(False, "negation_or_hedge", utterance)
    if " ".join(toks) in AFFIRMATION_WHITELIST:  # exact match, NOT substring
        return Affirmation(True, "whitelist_match", utterance)
    return Affirmation(False, "no_match", utterance)


# ---- capability-guarded receipt -------------------------------------------------------------
_SENTINEL = object()  # module-private; only this module can pass it


class ReceiptForgery(RuntimeError):
    pass


@dataclass(frozen=True)
class ConfirmationReceipt:
    field_id: str
    candidate_id: str
    candidate_fingerprint: str
    validation: ValidationReport
    affirmation: Affirmation
    _token: object = None

    def __post_init__(self):
        # Guards against ACCIDENTAL misuse (a helper drifting into the wrong module). It is not a
        # defence against deliberate frame/dataclass tampering — the AST test covers that.
        f = sys._getframe(1)
        while f is not None and f.f_code.co_name in ("__init__", "__post_init__"):
            f = f.f_back
        caller = f.f_globals.get("__name__") if f else None
        if self._token is not _SENTINEL or caller != __name__:
            raise ReceiptForgery(f"ConfirmationReceipt may only be issued by {__name__}, not {caller}")

    def to_dict(self):
        return {"field_id": self.field_id, "candidate_id": self.candidate_id,
                "candidate_fingerprint": self.candidate_fingerprint,
                "validation": self.validation.to_dict(), "affirmation": self.affirmation.to_dict()}


def confirm(candidate: Candidate, report: ValidationReport, utterance: str
            ) -> tuple[Affirmation, ConfirmationReceipt | None]:
    """Parse the user's reply to a read-back. Issues a receipt only for a passed report on this
    exact candidate AND an explicit affirmation."""
    aff = parse_affirmation(utterance)
    ok = (aff.explicit and report.passed and report.field_id == candidate.field_id
          and report.candidate_id == candidate.candidate_id and report.normalized_value)
    receipt = ConfirmationReceipt(
        candidate.field_id, candidate.candidate_id,
        fingerprint(candidate.field_id, report.normalized_value, candidate.candidate_id),
        report, aff, _SENTINEL) if ok else None
    events.emit("CONFIRMATION", field_id=candidate.field_id, candidate_id=candidate.candidate_id,
                affirmation=aff, receipt_issued=receipt is not None)
    return aff, receipt
