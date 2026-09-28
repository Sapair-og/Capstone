"""Normalization: removes presentation noise, never repairs a wrong value.
A short id is never padded, a bad checksum never corrected, an unlisted script never transliterated."""
from __future__ import annotations

import re

from .types import FieldSpec

_INVISIBLE = dict.fromkeys(map(ord, "​‌‍‎‏⁠﻿­"), None)
_SPACES = dict.fromkeys(map(ord, "   \t\n\r"), " ")
_DEVANAGARI = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}  # listed script for the Hindi channel
_SEP = re.compile(r"[\s\-.]")
_DATE = re.compile(r"^(\d{1,2})[/\-. ](\d{1,2})[/\-. ](\d{4})$")
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def base(v: str) -> str:
    v = (v or "").translate(_INVISIBLE).translate(_SPACES).translate(_DEVANAGARI)
    return re.sub(r" +", " ", v).strip()


def normalize(value: str, spec: FieldSpec, aliases: dict[str, str] | None = None) -> str:
    v = base(value)
    k = spec.kind
    if k in ("pan", "aadhaar", "pincode"):
        v = _SEP.sub("", v)
        return v.upper() if k == "pan" else v
    if k == "mobile":
        v = re.sub(r"[\s\-.()]", "", v)
        for pre in ("+91", "0091", "91", "0"):
            if v.startswith(pre) and len(v) - len(pre) == 10:
                return v[len(pre):]
        return v
    if k == "email":
        return v.replace(" ", "").lower()
    if k == "date":
        if m := _ISO.match(v):
            return f"{m[3]}/{m[2]}/{m[1]}"
        if m := _DATE.match(v):
            return f"{int(m[1]):02d}/{int(m[2]):02d}/{m[3]}"
        return v
    if k == "enum":
        key = v.casefold()
        for o in spec.options:
            if o.casefold() == key:
                return o
        return (aliases or {}).get(key, v)
    return v
