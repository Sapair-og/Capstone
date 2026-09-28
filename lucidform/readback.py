"""Read-back generator: phrase a validated value so it can be checked BY EAR (paper §III-D).
Identifiers are read character by character in paused groups; punctuation is spoken as words."""
from __future__ import annotations

import datetime as dt

from .types import FieldSpec

_GROUPS = {"aadhaar": (4, 4, 4), "mobile": (5, 5), "pincode": (3, 3), "pan": (5, 4, 1)}
_PUNCT = {",": "comma", ".": "dot", "/": "slash", "-": "dash", "#": "hash", "@": "at", "_": "underscore",
          "(": "open bracket", ")": "close bracket", "&": "and", "'": "apostrophe", "+": "plus"}
_WORDS_EN = "zero one two three four five six seven eight nine".split()
_WORDS_HI = "शून्य एक दो तीन चार पाँच छह सात आठ नौ".split()
PAUSE = " … "  # rendered as a pause by TTS; a visible separator in text mode


def _spell(s: str, lang: str) -> str:
    words = _WORDS_HI if lang == "hi" else _WORDS_EN
    return ", ".join(words[int(c)] if c.isdigit() else _PUNCT.get(c, c.upper()) for c in s)


def _grouped(v: str, sizes, lang) -> str:
    out, i = [], 0
    for n in sizes:
        out.append(_spell(v[i:i + n], lang)); i += n
    return PAUSE.join(out)


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def render(value: str, spec: FieldSpec, lang: str = "en") -> str:
    if spec.readback == "date":
        d, m, y = map(int, value.split("/"))
        return f"{_ordinal(d)} {dt.date(y, m, d):%B} {y}"
    if spec.kind in _GROUPS:
        return _grouped(value, _GROUPS[spec.kind], lang)
    if spec.readback == "chars":
        return _spell(value, lang)
    if spec.kind == "text":  # speak punctuation a synthesizer would otherwise skip
        return "".join(f" {_PUNCT[c]} " if c in _PUNCT else c for c in value).replace("  ", " ").strip()
    return value


def prompt(value: str, spec: FieldSpec, lang: str = "en") -> str:
    label = spec.field_id.replace("_", " ")
    body = render(value, spec, lang)
    return (f"मैंने आपका {label} सुना: {body}. क्या यह सही है?" if lang == "hi"
            else f"I have your {label} as: {body}. Is that correct?")
