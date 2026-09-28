# AGENTS.md — handoff for any AI agent (Claude, Codex, Cursor, Gemini…) or new teammate

Read this file, then `ROADMAP.md` (humans: `docs/TEAM_GUIDE.md`), then `docs/PROGRESS.md`. If `graphify-out/GRAPH_REPORT.md`
exists, read it before opening source files and prefer `graphify query "<question>"` /
`graphify explain "<Symbol>"` over grepping.

## What this is
LucidForm: a voice/text assistant that fills Indian KYC-style forms for low-literacy and
visually-impaired users. Source of truth for the design is the capstone paper
(`docs/paper/` if present) — section refs like §III-B below point into it.

**Core rule: the LLM never writes a value into the form.**
```
Parser → Orchestrator → Extraction (LLM) → [VALIDATION GATE] → Read-back → Confirm → Commit
```

## Code map
| File | Role | Paper |
|---|---|---|
| `lucidform/types.py` | `Candidate` (frozen proposal), `FieldSpec`, `ValidationReport`, `Reason` (ordered taxonomy), `Affirmation` | §III |
| `lucidform/validation.py` | deterministic gate, 9 checks in fixed order, first failure wins | §III-B, Alg. 2 |
| `lucidform/normalize.py` | strips noise, never repairs (no padding, no checksum fix, no transliteration) | §III-B |
| `lucidform/checksums.py` | Verhoeff (Aadhaar) | §II |
| `lucidform/rules_data.py` | states list, PIN-prefix → state map | — |
| `lucidform/confirmation.py` | whole-utterance whitelist parser; **only** place a `ConfirmationReceipt` is built | §III-D, §III-E2, Alg. 3 |
| `lucidform/form_state.py` | `FormState.commit` = **only** write path; re-verifies receipt + SHA-256 fingerprint | §III-E1, Alg. 1 |
| `lucidform/fingerprint.py` | sha256(field ‖ normalized value ‖ candidate_id) | Alg. 1 |
| `lucidform/readback.py` | ear-checkable read-back (grouped digits, spoken punctuation, EN/HI) | §III-D |
| `lucidform/spec.py` + `overlays/*.yaml` | human-authored semantic overlay → `FormSpec` | §IV-A |
| `lucidform/events.py` | append-only JSONL log (`LUCIDFORM_LOG=path`) | §IV-D |
| `tests/archcheck.py` | AST safety check (rules R1–R3 below) | §III-E3 |
| `tests/corpora/*.yaml` | adversarial suites: gate 56 cases, confirmation 49 | §IV-C |

## Invariants — never break these (CI enforces most)
1. **R1** `validation`, `form_state`, `confirmation` never import a model client (`anthropic`, `openai`, `langgraph`, `lucidform.extraction`, `lucidform.llm`, `lucidform.orchestrator`, `lucidform.agents`), even transitively. So LLM code lives in `extraction.py` / `llm.py` / `orchestrator.py` / `agents/`.
2. **R2** `ConfirmationReceipt(...)` is only constructed in `confirmation.py`.
3. **R3** Nothing outside `form_state.py` touches `FormState._values`.
4. Adding a gate rule means adding cases to `tests/corpora/gate_cases.yaml` too, including at least one ACCEPT control.
5. Report gate recall only together with its false-positive rate. Offline replay never produces an extraction-accuracy number.
6. All personal data is synthetic. Aadhaar-format numbers are generated with `checksums.verhoeff_digit`.

## Run
```bash
pip install -e ".[dev,pdf]" && pytest -q -s
```

## Working rules for agents
- Work only on your phase branch (`phase-N-<slug>`). Open a PR to `main`, and don't push to `main` directly.
- Before you finish a session, append an entry to `docs/PROGRESS.md` covering what you did, what's left, and any gotchas. That file is the memory shared across people and agents.
- Keep the code compact and typed. Keep the tests beside it.
