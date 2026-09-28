"""Gate adversarial suite: every case must produce its declared outcome, and the false-positive
rate is reported alongside recall — never recall alone."""
import pytest

from conftest import TODAY, corpus
from lucidform.types import Candidate
from lucidform.validation import validate

CASES = corpus("gate_cases.yaml")


def _run(c, form):
    cand = Candidate(c["field"], c["value"], confidence=c.get("confidence", 0.95),
                     ambiguous=c.get("ambiguous", False), grounded=c.get("grounded", True))
    return validate(cand, form, c.get("confirmed", {}), today=TODAY)


def test_corpus_shape():
    assert len(CASES) == 56
    assert len({c["cat"] for c in CASES}) == 11
    assert len({c["id"] for c in CASES}) == 56
    controls = sum(c["expect"] == "ACCEPT" for c in CASES)
    assert controls >= 11, "about a fifth of the suite must be accept-controls"


@pytest.mark.parametrize("c", CASES, ids=[c["id"] for c in CASES])
def test_gate_case(c, form):
    rep = _run(c, form)
    got = "ACCEPT" if rep.passed else rep.reason.value
    assert got == c["expect"], f"{c['id']}: {c['value']!r} -> {got} ({rep.detail})"


def test_recall_and_false_positive_rate(form):
    res = [(c["expect"] == "ACCEPT", _run(c, form).passed) for c in CASES]
    neg = [p for ctrl, p in res if not ctrl]
    pos = [p for ctrl, p in res if ctrl]
    recall = sum(not p for p in neg) / len(neg)
    fpr = sum(not p for p in pos) / len(pos)
    print(f"\ngate recall={recall:.0%} over {len(neg)}; false-positive rate={fpr:.0%} over {len(pos)} controls")
    assert recall == 1.0 and fpr == 0.0
