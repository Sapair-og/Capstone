# LucidForm — build roadmap

Each phase lands as its own commit(s) with tests green. The safety kernel comes first so every
later stage is built *against* the guarantees rather than having them bolted on.

| Phase | Scope | Depends on | Owner | Branch | Status |
|---|---|---|---|---|---|
| **0** | Repo scaffold, packaging, append-only event log, CI | — | Yash | main | ✅ done |
| **1** | Safety kernel: types, Verhoeff, 9-reason gate, confirmation whitelist, guarded receipt, single-write `FormState`, read-back, AST safety test, adversarial corpora (56/49) | 0 | Yash | main | ✅ done |
| **2** | Form layer: generate KYC AcroForm PDF, parse fields + MaxLen by walking widget annotations, merge with overlay, single PDF write path, final-review pass | 1 | _proposed: Yash_ | `phase-2-form` | ⏳ next |
| **3** | Extraction: schema-bounded LLM call (intent, value, quote, confidence, ambiguous, alternatives), grounding + confidence clamping, offline replay + live Anthropic backend | 1 | _proposed: friend_ | `phase-3-extraction` | ⏳ next (parallel with 2) |
| **4** | Orchestrator: per-field LangGraph loop, help/jargon branch, text CLI, 3 synthetic personas, end-to-end sessions, layered-defense report (Table II) | 2, 3 | _proposed: Yash_ | `phase-4-orchestrator` | ☐ |
| **5** | Channels: Hindi prompts/read-back, voice (STT/TTS) behind channel abstraction, identifier round-trip probe | 4 | _proposed: friend_ | `phase-5-voice-hindi` | ☐ |
| **6** | Ingestion + extras: OCR/layout for scanned forms, search/help agent, optional accessible web UI | 4 | _proposed: Yash_ | `phase-6-ocr-ui` | ☐ (parallel with 5) |
| **7** | Evaluation: analysis over recorded logs, live-model extraction accuracy, paper figures | 5, 6 | _proposed: friend_ | `phase-7-eval` | ☐ |

## Invariants every phase must keep
1. The LLM never writes a value. `FormState.commit` is the only mutation and it re-verifies everything.
2. `validation`, `form_state`, `confirmation` never import a model client (checked by `tests/archcheck.py`).
3. Receipts are only constructed in `confirmation.py`.
4. Gate recall is never reported without its false-positive rate.
5. Offline replay never produces an extraction-accuracy claim.
