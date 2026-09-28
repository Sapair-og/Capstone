# LucidForm — build roadmap

Each phase lands as its own commit(s) with tests green. The safety kernel comes first so every
later stage is built *against* the guarantees rather than having them bolted on.

| Phase | Scope | Status |
|---|---|---|
| **0** | Repo scaffold, packaging, append-only event log, CI | ✅ done |
| **1** | Safety kernel: types, Verhoeff, 9-reason validation gate, confirmation whitelist, capability-guarded receipt, single-write-path `FormState`, read-back renderer, AST safety test, adversarial corpora (56 gate / 49 confirmation) | ✅ done |
| **2** | Form layer: generate the KYC AcroForm PDF, parse fields + MaxLen by walking widget annotations, merge with overlay, single PDF write path, final-review pass | ⏳ next |
| **3** | Extraction: schema-bounded LLM call (intent, value, quote, confidence, ambiguous, alternatives), grounding + confidence clamping, offline replay backend, live Anthropic backend | ☐ |
| **4** | Orchestrator: per-field loop (LangGraph state machine per workflow diagram), help/jargon branch, text channel CLI, 3 synthetic personas, end-to-end sessions, layered-defense report (Table II) | ☐ |
| **5** | Channels: Hindi prompts/read-back, voice channel (STT/TTS) behind the channel abstraction, identifier round-trip probe | ☐ |
| **6** | Ingestion + extras: OCR/layout path for scanned forms, search/help agent, optional accessible web UI | ☐ |
| **7** | Evaluation + paper numbers: analysis over recorded logs only, live-model extraction accuracy, figures for the paper | ☐ |

## Invariants every phase must keep
1. The LLM never writes a value. `FormState.commit` is the only mutation and it re-verifies everything.
2. `validation`, `form_state`, `confirmation` never import a model client (checked by `tests/archcheck.py`).
3. Receipts are only constructed in `confirmation.py`.
4. Gate recall is never reported without its false-positive rate.
5. Offline replay never produces an extraction-accuracy claim.
