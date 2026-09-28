"""Load a semantic overlay into FieldSpecs. Phase 2's PDF parser merges structural facts
(e.g. MaxLen read from the AcroForm) on top of these via `merge_structural`."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from . import rules_data
from .types import FieldSpec

_EXTRA = ("aliases", "min_age", "max_age", "checksum")  # overlay keys kept outside FieldSpec


@dataclass(frozen=True)
class FormSpec:
    form_id: str
    title: str
    fields: tuple[FieldSpec, ...]
    extras: dict[str, dict[str, Any]] = field(default_factory=dict)
    confidence_threshold: float = 0.6

    def get(self, fid: str) -> FieldSpec:
        return next(f for f in self.fields if f.field_id == fid)

    def extra(self, fid: str, key: str, default: Any = None) -> Any:
        return self.extras.get(fid, {}).get(key, default)

    @property
    def ids(self) -> list[str]:
        return [f.field_id for f in self.fields]


def load_overlay(path: str | Path | None = None) -> FormSpec:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8") if path else
                         resources.files("lucidform.overlays").joinpath("kyc_individual.yaml").read_text(encoding="utf-8"))
    specs, extras = [], {}
    for f in raw["fields"]:
        f = dict(f)
        if src := f.pop("options_from", None):
            f["options"] = getattr(rules_data, src)
        extras[f["field_id"]] = {k: f.pop(k) for k in _EXTRA if k in f}
        f["options"] = tuple(f.get("options", ()))
        f["cross"] = tuple(f.get("cross", ()))
        specs.append(FieldSpec(**f))
    return FormSpec(raw["form_id"], raw.get("title", raw["form_id"]), tuple(specs), extras,
                    raw.get("confidence_threshold", 0.6))


def merge_structural(form: FormSpec, structural: dict[str, dict[str, Any]]) -> FormSpec:
    """Structural facts from the PDF win for max_length (the document is the ground truth)."""
    fs = tuple(replace(f, max_length=structural[f.field_id].get("max_length") or f.max_length)
               if f.field_id in structural else f for f in form.fields)
    return replace(form, fields=fs)
