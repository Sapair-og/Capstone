import re

import pytest

from conftest import corpus
from lucidform.confirmation import parse_affirmation

CASES = corpus("confirmation_cases.yaml")


def naive_parser(u: str) -> bool:
    """The plausible-but-wrong design: search for an affirmative substring."""
    return any(t in u.lower() for t in ("yes", "correct", "right", "haan", "sahi", "हाँ"))


def test_corpus_shape():
    assert len(CASES) == 49
    assert len({c["cat"] for c in CASES}) == 7
    assert sum(c["expect"] for c in CASES) == 13


@pytest.mark.parametrize("c", CASES, ids=[c["id"] for c in CASES])
def test_confirmation_case(c):
    a = parse_affirmation(c["u"])
    assert a.explicit is c["expect"], f"{c['id']}: {c['u']!r} -> {a.basis}"


def test_suite_discriminates_naive_parser():
    """The suite must NOT be satisfiable by the naive design."""
    fails = [c["id"] for c in CASES if naive_parser(c["u"]) != c["expect"]]
    print(f"\nnaive substring parser fails {len(fails)}/49: {fails}")
    assert len(fails) >= 8
