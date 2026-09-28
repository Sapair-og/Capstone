# Team guide — how the two of us build LucidForm

This guide is for Yash and his teammate. Read it once. After that, `CONTRIBUTING.md` is the short command reference.

## 1. The idea in 60 seconds
LucidForm helps people who can't easily read a form fill in a KYC form by talking. The twist,
and the thing the paper is about, is that **the AI never writes into the form.** It only
*proposes* a value. A plain, non-AI checker validates it (format, Aadhaar checksum, PAN-vs-surname,
PIN-vs-state). The value is read back to the user, and it's saved only when the user clearly says "yes".
Three separate mechanisms make it impossible for code to skip those steps, and the test suite
proves that each one catches a violation.

```
PDF form → Orchestrator → LLM extraction → [VALIDATION GATE] → Read-back → "yes" → Commit → filled PDF
```
Phases 0–1 (the gate, confirmation, commit path, and tests) are **done and on `main`**. The rest is split below.

## 2. Who does what
The harder, open-ended phases (LLM, agent loop, speech) go to the teammate. The more contained
phases (PDF, OCR, evaluation) go to Yash. Each round, both of us work in parallel on phases that
don't block each other.

| Round | Yash | Teammate | Why this order |
|---|---|---|---|
| **1** | **P2 Form layer**: generate the KYC PDF, read its fields, write values back | **P3 Extraction**: LLM call with a strict JSON schema, grounding, confidence clamping, offline replay | Neither needs the other. Both only need Phase 1. |
| **2** | **P6 Ingestion**: OCR a scanned/photographed form into the same field schema, plus the help-text content ("where do I find my PAN?") | **P4 Orchestrator**: LangGraph per-field loop wiring P2 + P3 + gate + confirm, text CLI, personas, end-to-end sessions | P4 needs P2 and P3 merged. P6 only needs P2. |
| **3** | **P7 Evaluation**: log analysis scripts, larger persona corpus, Table II / paper figures, optional web UI | **P5 Voice + Hindi**: STT/TTS behind the channel interface, Hindi read-back, identifier round-trip probe | P7 reads the logs P4 produces. P5 plugs into P4's channel interface. |

**Hardness, roughly:** P4 > P5 > P3 > P6 > P2 ≈ P7. If one of us finishes a round early, pick up
tests or corpus cases for the other's phase rather than starting the next round alone.

## 3. Setup (each person, once, ~15 min)
You need Git, Python 3.11+, and **Claude Code**, which is included in the Claude Pro plan. Install
it from claude.com/claude-code. Claude Code works directly in the repo folder, can run the tests,
and can push. The chat app can't do that.

```bash
git clone https://github.com/Sapair-og/Capstone && cd Capstone
python -m venv .venv
.venv\Scripts\activate            # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -e ".[dev,pdf]"
pytest -q                          # expect all green

pip install uv
uv tool install graphifyy          # the PyPI name has two y's
graphify install --project         # adds the /graphify skill + a hook that makes Claude use the graph
graphify hook install              # rebuilds the graph automatically on every commit
git config alias.gpull "!git pull && graphify update ."
```
The repo owner (Yash) adds the teammate under **GitHub → repo → Settings → Collaborators**.
It's also worth turning on **Settings → Branches → protect `main` → require a pull request +
passing checks**, so nobody (human or AI) pushes broken code to `main`.

## 4. The loop for every phase
```bash
git switch main && git gpull                   # latest main + refreshed graph
git switch -c phase-3-extraction               # one branch per phase
claude                                         # start Claude Code in the repo, then paste the starter prompt (§5)
pytest -q                                      # green before every push
git push -u origin phase-3-extraction          # open a Pull Request on GitHub
```
- The **other person reviews the PR** (skim it and run the tests) and merges it.
- After any merge, run `git switch main && git gpull`. Then, on your own branch, run `git rebase main`.
- Commit small and often. Don't hand-edit someone else's phase files. If you need a change there,
  ask them or open a tiny separate PR.
- Before ending a session, have Claude **append an entry to `docs/PROGRESS.md`**
  (what's done, what's left, gotchas) and push. This is how the other person's AI catches up.

## 5. Saving tokens with graphify
**The problem:** every new AI session starts blind, and it burns tokens reading every file to
understand the project. **The fix:** graphify turns the repo (code *and* the paper PDFs in
`docs/paper/`) into a knowledge graph once. After that, the AI asks the graph small questions
and doesn't have to read files.

**What gets committed.** Only `graphify-out/graph.json`, `GRAPH_REPORT.md` and `manifest.json`.
`.gitignore` is already set up for this. When you pull, you get the latest graph without
rebuilding it.

**Build or refresh the graph:**
```bash
graphify update .        # code only: local, free, seconds
# inside Claude Code:
/graphify . --update     # also re-reads changed docs/PDFs (this part uses model tokens, so only after doc changes)
```

**Query it yourself** (free, no AI involved). This is also the quickest way to understand
a part of the code before you prompt:
```bash
graphify query "how does a value get committed to the form?"
graphify explain "FormState"
graphify path "Candidate" "ConfirmationReceipt"
```

**Starter prompt.** Paste this at the start of *every* Claude Code session:
```text
You're working on LucidForm, phase <N> (<name>), branch phase-<N>-<slug>.
Read AGENTS.md, the last two entries of docs/PROGRESS.md, and graphify-out/GRAPH_REPORT.md.
Don't open source files to explore. Use `graphify query` / `graphify explain` / `graphify path`
first, then read only the specific functions or line ranges you need.
Follow the invariants in AGENTS.md. Keep pytest green (especially tests/test_architecture.py).
Plan this phase in small steps, show me the plan, then do step 1.
At the end: append to docs/PROGRESS.md, commit, and push the branch.
```

**More habits that save tokens:**
- **One phase per session.** When a session gets long, end it (write the PROGRESS entry and push)
  and start fresh with the starter prompt. A new session plus the graph is cheaper than a huge
  old context.
- If Claude keeps reading whole files anyway, reinstall with `graphify install --project --strict`.
  That blocks the first raw file read of each session and redirects it to the graph.
- **Using the Claude chat app, or a different AI with no repo access?** Paste `AGENTS.md` +
  `graphify-out/GRAPH_REPORT.md` + the latest PROGRESS entry. That's usually enough context for
  design questions, without pasting any code.
- Ask narrow questions ("change `_cross` in validation.py to also…"). Avoid broad ones ("look at the project and…").

## 6. Rules nobody (human or AI) breaks
Full list in `AGENTS.md`. The short version:
1. The LLM never writes a value. Only `FormState.commit()` writes, and it re-checks everything.
2. `validation.py`, `form_state.py`, `confirmation.py` never import any AI/LLM library. So LLM code lives in
   `extraction.py`, `llm.py`, `orchestrator.py` or `agents/`. The test suite fails the build otherwise.
3. Every new validation rule gets test cases in `tests/corpora/gate_cases.yaml`, including one that must be accepted.
4. All names and ID numbers are fake. Never put a real Aadhaar/PAN anywhere.

## 7. Message to send your teammate
> Hey! The capstone repo is ready: https://github.com/Sapair-og/Capstone. I've added you as a collaborator.
> Phases 0–1 (the core safety part) are done and tested. Please read `docs/TEAM_GUIDE.md` first:
> it has setup, the phase split, and how we use graphify so Claude doesn't burn tokens re-reading the code.
> I've given you the heavier phases (P3 extraction, P4 orchestrator, P5 voice/Hindi) since you're
> stronger on that side. I'm doing P2 (PDF), P6 (OCR) and P7 (evaluation).
> Round 1: I take P2, you take P3, in parallel. One branch per phase, PRs into main, and we review each other.
