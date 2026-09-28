# LucidForm — build roadmap

Each phase lands as its own commit(s) with tests green. The safety kernel comes first so every
later stage is built *against* the guarantees rather than having them bolted on.

| Phase | Scope | Depends on | Owner | Branch | Status |
|---|---|---|---|---|---|
| **0** | Repo scaffold, packaging, append-only event log, CI | — | Yash | main | ✅ done |
| **1** | Safety kernel: types, Verhoeff, 9-reason gate, confirmation whitelist, guarded receipt, single-write `FormState`, read-back, AST safety test, adversarial corpora (56/49) | 0 | Yash | main | ✅ done |
| **2** | Form layer: generate KYC AcroForm PDF, parse fields + MaxLen by walking widget annotations, merge with overlay, single PDF write path, final-review pass | 1 | Yash | `phase-2-form` | ⏳ round 1 |
| **3** | Extraction: schema-bounded LLM call (intent, value, quote, confidence, ambiguous, alternatives), grounding + confidence clamping, offline replay + live Anthropic backend | 1 | Teammate | `phase-3-extraction` | ⏳ round 1 |
| **4** | Orchestrator: per-field LangGraph loop, help/jargon branch, channel interface, text CLI, 3 synthetic personas, end-to-end sessions | 2, 3 | Teammate | `phase-4-orchestrator` | ☐ round 2 |
| **6** | Ingestion: OCR/layout for scanned or photographed forms → same field schema; help-text content for the search/help agent | 2 | Yash | `phase-6-ocr` | ☐ round 2 |
| **5** | Channels: Hindi prompts/read-back, voice (STT/TTS) behind the channel interface, identifier round-trip probe | 4 | Teammate | `phase-5-voice-hindi` | ☐ round 3 |
| **7** | Evaluation: analysis over recorded logs, larger persona corpus, layered-defense Table II, live-model extraction accuracy, paper figures, optional web UI | 4 (final numbers after 5) | Yash | `phase-7-eval` | ☐ round 3 |

Difficulty (roughly): P4 > P5 > P3 > P6 > P2 ≈ P7. See `docs/TEAM_GUIDE.md` for the round plan.

## Invariants every phase must keep
1. The LLM never writes a value. `FormState.commit` is the only mutation and it re-verifies everything.
2. `validation`, `form_state`, `confirmation` never import a model client (checked by `tests/archcheck.py`).
3. Receipts are only constructed in `confirmation.py`.
4. Gate recall is never reported without its false-positive rate.
5. Offline replay never produces an extraction-accuracy claim.
