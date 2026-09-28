# Graph Report - Capstone  (2026-09-28)

## Corpus Check
- 39 files · ~20,355 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 271 nodes · 490 edges · 24 communities (16 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a6bb5b0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- types.py
- test_commit_path.py
- What You Must Do When Invoked
- test_units.py
- FormState
- Candidate
- validation.py
- conftest.py
- test_architecture.py
- events.py
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- Team workflow (2+ people, each with their own Claude)
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- Progress log
- CLAUDE.md
- .claude/CLAUDE.md
- extraction-spec.md
- lucidform

## God Nodes (most connected - your core abstractions)
1. `Candidate` - 19 edges
2. `FormState` - 16 edges
3. `FormSpec` - 16 edges
4. `_Ctx` - 16 edges
5. `FieldSpec` - 15 edges
6. `_flow()` - 14 edges
7. `ConfirmationReceipt` - 13 edges
8. `validate()` - 13 edges
9. `What You Must Do When Invoked` - 12 edges
10. `confirm()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Invariants — never break these (CI enforces most)` --references--> `verhoeff_digit()`  [INFERRED]
  AGENTS.md → lucidform/checksums.py
- `Code map` --references--> `ConfirmationReceipt`  [INFERRED]
  AGENTS.md → lucidform/confirmation.py
- `The guarantee, enforced three ways` --references--> `ConfirmationReceipt`  [INFERRED]
  README.md → lucidform/confirmation.py
- `Step 2.5 - Transcribe video / audio files (only if video files detected)` --references--> `base()`  [INFERRED]
  .claude/skills/graphify/references/transcribe.md → lucidform/normalize.py
- `Code map` --references--> `Candidate`  [INFERRED]
  AGENTS.md → lucidform/types.py

## Import Cycles
- None detected.

## Communities (24 total, 8 thin omitted)

### Community 0 - "types.py"
Cohesion: 0.10
Nodes (27): Code map, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), dataclasses, Enum, importlib, Form state. No public setter. `commit` is the single write path (Algorithm 1)…, LucidForm — the LLM may interpret a user's speech, never write a value into the… (+19 more)

### Community 1 - "test_commit_path.py"
Cohesion: 0.14
Nodes (25): confirm(), ConfirmationReceipt, parse_affirmation(), Confirmation parser (Algorithm 3) and the only place a ConfirmationReceipt can…, Parse the user's reply to a read-back. Issues a receipt only for a passed…, ReceiptForgery, _tokens(), recent() (+17 more)

### Community 2 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 3 - "test_units.py"
Cohesion: 0.13
Nodes (21): AGENTS.md — handoff for any AI agent (Claude, Codex, Cursor, Gemini…) or new teammate, Invariants — never break these (CI enforces most), Run, What this is, Working rules for agents, itertools, Verhoeff check digit (dihedral group D5). Used by Aadhaar; catches all single-…, Check digit to append to `body` (used only to fabricate synthetic test… (+13 more)

### Community 4 - "FormState"
Cohesion: 0.11
Nodes (11): hashlib, fingerprint(), Binds a receipt to one exact (field, value, candidate). Recomputed at commit,…, FormState, Layout, LucidForm, Run, The guarantee, enforced three ways (+3 more)

### Community 5 - "Candidate"
Cohesion: 0.15
Nodes (12): date, Candidate, Any, A proposal from extraction. Never a value the system holds as fact., ValidationReport, validate(), test_unconfirmed_value_cannot_influence_cross_field(), parametrize (+4 more)

### Community 6 - "validation.py"
Cohesion: 0.18
Nodes (16): Static reference data for deterministic rules ("Validation Rules DB" in the…, states_for_pincode(), _ambiguous(), _checksum(), _confidence(), _cross(), _Ctx, _empty() (+8 more)

### Community 7 - "conftest.py"
Cohesion: 0.14
Nodes (15): datetime, clear_memory(), pytest, re, _clean_events(), corpus(), form(), fixture (+7 more)

### Community 8 - "test_architecture.py"
Cohesion: 0.18
Nodes (14): AST, pathlib, shutil, check(), _imports(), _modname(), Path, Static-analysis safety check (paper §III-E3). Parses the package AST and… (+6 more)

### Community 9 - "events.py"
Cohesion: 0.26
Nodes (11): json, emit(), _jsonable(), _path(), Any, Append-only, timestamped event log. Every pipeline stage emits here (paper…, read_log(), os (+3 more)

### Community 10 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 11 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 12 - "Team workflow (2+ people, each with their own Claude)"
Cohesion: 0.33
Nodes (5): Handing off to any other AI, One-time setup (each person), Per phase, Sharing the graph, Team workflow (2+ people, each with their own Claude)

### Community 13 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 14 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 15 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **54 isolated node(s):** `lucidform`, `graphify`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 121 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Candidate` connect `Candidate` to `types.py`, `test_commit_path.py`, `FormState`, `validation.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `FormSpec` connect `types.py` to `FormState`, `Candidate`, `validation.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `FormState` connect `FormState` to `types.py`, `test_commit_path.py`, `Candidate`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Candidate` (e.g. with `Code map` and `confirm()`) actually correct?**
  _`Candidate` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `FormState` (e.g. with `ConfirmationReceipt` and `FormSpec`) actually correct?**
  _`FormState` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `FormSpec` (e.g. with `Code map` and `FormState`) actually correct?**
  _`FormSpec` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `_Ctx` (e.g. with `FormSpec` and `Candidate`) actually correct?**
  _`_Ctx` has 3 INFERRED edges - model-reasoned connections that need verification._