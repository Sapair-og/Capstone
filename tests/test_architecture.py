"""Architectural enforcement (paper §III-E3). The build fails if the codebase violates any rule —
and each rule is proven to FIRE on a deliberate violation, because a safety test that has never
been observed to fail is not evidence that it works."""
import shutil
from pathlib import Path

import pytest

import lucidform
from archcheck import check

PKG = Path(lucidform.__file__).parent


def test_codebase_is_clean():
    v = check(PKG)
    assert not v, "\n".join(v)


@pytest.fixture
def clone(tmp_path):
    dst = tmp_path / "lucidform"
    shutil.copytree(PKG, dst, ignore=shutil.ignore_patterns("__pycache__"))
    return dst


VIOLATIONS = {
    "R1_direct": ("validation.py", "import anthropic\n"),
    "R1_transitive": ("normalize.py", "from . import llm\n"),  # validation -> normalize -> llm
    "R1_form_state": ("form_state.py", "from openai import OpenAI\n"),
    "R2_construct": ("form_state.py", "ConfirmationReceipt('a','b','c',None,None)\n"),
    "R2_sentinel": ("readback.py", "from .confirmation import _SENTINEL\n"),
    "R3_private": ("readback.py", "def f(s):\n    s._values['pan'] = 'X'\n"),
    "R3_reflection": ("readback.py", "def f(s):\n    getattr(s, '_values')['pan'] = 'X'\n"),
}


@pytest.mark.parametrize("name", VIOLATIONS)
def test_rule_fires_on_violation(clone, name):
    fname, code = VIOLATIONS[name]
    if name == "R1_transitive":
        (clone / "llm.py").write_text("import anthropic\n")
    p = clone / fname
    p.write_text(p.read_text() + "\n" + code)
    v = check(clone)
    rule = name.split("_")[0]
    hits = [x for x in v if f" {rule} " in x]
    assert hits, f"{name} not detected"
    assert all(":" in h.split(f" {rule} ")[0] for h in hits), "must name file and line"
