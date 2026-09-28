# Progress log

Append-only. Add the newest entry at the bottom. Each entry covers: who, phase, what you did, what's left, and gotchas.

---
### 2026-09-28 · Yash (+Claude) · Phases 0–1
- **Done:** scaffold, event log, CI, and the full safety kernel (gate, confirmation, receipt, FormState, read-back, AST check). 133 tests are green. Gate has 100% recall with 0% FPR on 11 controls. The naive parser fails 20 of 49 cases.
- **Also:** added AGENTS.md, CLAUDE.md, CONTRIBUTING.md, the graphify config, and the owner/dependency columns in ROADMAP.
- **Next:** Phase 2 (form/PDF) and Phase 3 (extraction) are independent and can run in parallel.
- **Gotchas:** pypdf's high-level `get_fields()` drops `/MaxLen` (paper §IV-A), so Phase 2 has to walk `/Annots` widgets directly. The receipt frame-guard only catches accidental misuse. Deliberate bypass is caught by `tests/archcheck.py`.
