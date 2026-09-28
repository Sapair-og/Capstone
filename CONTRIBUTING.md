# Team workflow (2+ people, each with their own Claude)

Your Claude accounts don't share memory or projects, so **the repo is the only shared brain**.
Everything an agent needs lives in `AGENTS.md`, `ROADMAP.md`, `docs/PROGRESS.md`, and the
graphify graph.

## One-time setup (each person)
```bash
git clone https://github.com/Sapair-og/Capstone && cd Capstone
python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev,pdf]"
uv tool install graphifyy        # or: pipx install graphifyy
graphify install --project       # registers the /graphify skill for this repo
graphify hook install            # rebuilds the graph on every commit (AST only, no API cost)
git config alias.gpull '!git pull && graphify update .'
```
The repo owner adds each teammate under **GitHub → Settings → Collaborators**.

## Per phase
```bash
git switch main && git gpull
git switch -c phase-3-extraction          # the branch name matches the ROADMAP row
# ...work with your Claude, committing small and often...
pytest -q                                 # must be green
# append an entry to docs/PROGRESS.md
git push -u origin phase-3-extraction     # then open a PR to main; the other person reviews
```
- **Claim a phase** by putting your name in its ROADMAP `Owner` cell (in a tiny PR or a commit to main) before you start. That way nobody builds the same phase twice.
- Phases that don't depend on each other can run in parallel (see the ROADMAP `Depends on` column).
- After a PR merges, the other person runs `git gpull` and rebases their branch: `git rebase main`.
- Conflicts in `graph.json` resolve themselves (graphify installs a merge driver). For `docs/PROGRESS.md`, keep both entries.

## Sharing the graph
Commit only the queryable outputs: `graphify-out/graph.json`, `GRAPH_REPORT.md` and `manifest.json`
(`.gitignore` already allows exactly these). After changing docs or the paper, run `/graphify . --update`.

## Handing off to any other AI
Tell it to "read AGENTS.md, then docs/PROGRESS.md, then graphify-out/GRAPH_REPORT.md, and continue
phase N". That's enough context to carry on without the original chat.
