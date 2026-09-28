# LucidForm

**A deterministically gated architecture for safe LLM-assisted form filling** — VIT Bhopal capstone.

Government and banking forms (KYC, loans, insurance) are a barrier for low-literacy and
visually-impaired users. An LLM can hold the conversation, but in LucidForm it **never holds
write authority**: every candidate value passes a deterministic validation gate, is read back in
a form the user can check by ear, and is committed only on an explicit, whitelisted "yes".

```
Parser → Orchestrator → Extraction (LLM) → [ VALIDATION GATE ] → Read-back → Confirm → Commit
```

## The guarantee, enforced three ways
| Mechanism | Where | Catches |
|---|---|---|
| **Structural** — no public setter; `commit()` re-verifies receipt, report, affirmation and recomputes a SHA-256 fingerprint of (field, value, candidate) | `lucidform/form_state.py` | a receipt reused for a different value / field / candidate |
| **Capability** — `ConfirmationReceipt` needs a module-private sentinel + caller-frame check | `lucidform/confirmation.py` | accidental receipt construction elsewhere |
| **Architectural** — AST test fails the build on model-client imports into the gate, receipts built outside confirmation, or `_values` access | `tests/archcheck.py` | deliberate circumvention, at review time |

Each rule is proven to **fire** on a deliberate violation (`tests/test_architecture.py`).

## Layout
```
lucidform/
  types.py          Candidate, FieldSpec, ValidationReport, Reason taxonomy
  validation.py     the gate: EMPTY → TYPE_MISMATCH → FORMAT → ENUM → CHECKSUM → RANGE → CROSS_FIELD → AMBIGUOUS → LOW_CONFIDENCE
  checksums.py      Verhoeff (Aadhaar)
  normalize.py      presentation cleanup that never repairs a value
  confirmation.py   whole-utterance whitelist parser + receipt issuance
  form_state.py     single write path
  readback.py       ear-checkable read-back (grouped digits, spoken punctuation, EN/HI)
  events.py         append-only JSONL event log (set LUCIDFORM_LOG)
  overlays/         human-authored semantic overlay per form type
tests/corpora/      adversarial suites: 56 gate cases (11 categories), 49 confirmation cases (7)
```

## Run
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q -s        # prints gate recall + false-positive rate, and naive-parser failure count
```

All identities and identifiers in this repo are **synthetic**. See [ROADMAP.md](ROADMAP.md) for phase status.

**Team:** Shubh Pratap Singh · Yashvardhan Singh Sarangdevot · Lakshay Gupta · Kanishka Jain · Sanjith
