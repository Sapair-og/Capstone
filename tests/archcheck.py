"""Static-analysis safety check (paper §III-E3). Parses the package AST and reports:
  R1  validation/form-state import a model client (directly or transitively)
  R2  ConfirmationReceipt constructed (or the sentinel touched) outside confirmation.py
  R3  FormState's private `_values` accessed outside form_state.py
Returns 'path:line: RULE message' strings; empty list == clean."""
from __future__ import annotations

import ast
from pathlib import Path

PROTECTED = ("validation", "form_state", "confirmation")
FORBIDDEN_ROOTS = {"anthropic", "openai", "langchain", "langchain_core", "langgraph", "google", "groq",
                   "httpx", "requests", "litellm"}
FORBIDDEN_INTERNAL = {"extraction", "llm", "orchestrator", "agents"}  # package modules that hold model clients


def _modname(root: Path, path: Path) -> str:
    rel = path.relative_to(root.parent).with_suffix("")
    parts = list(rel.parts)
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def _imports(tree: ast.AST, mod: str, is_pkg: bool) -> list[tuple[str, int]]:
    out, pkg = [], mod if is_pkg else mod.rpartition(".")[0]
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out += [(a.name, n.lineno) for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                base = pkg.split(".")
                base = base[: len(base) - (n.level - 1)]
                target = ".".join(base + ([n.module] if n.module else []))
            else:
                target = n.module or ""
            out.append((target, n.lineno))
            out += [(f"{target}.{a.name}", n.lineno) for a in n.names]  # `from . import x`
    return out


def check(root: str | Path) -> list[str]:
    root = Path(root)
    pkg = root.name
    files = {_modname(root, p): p for p in root.rglob("*.py")}
    trees = {m: ast.parse(p.read_text(encoding="utf-8"), str(p)) for m, p in files.items()}
    graph = {m: _imports(t, m, files[m].name == "__init__.py") for m, t in trees.items()}
    v: list[str] = []

    def forbidden(name: str) -> bool:
        parts = name.split(".")
        return parts[0] in FORBIDDEN_ROOTS or (parts[0] == pkg and len(parts) > 1 and parts[1] in FORBIDDEN_INTERNAL)

    # R1 — transitive import closure of each protected module
    for start in (f"{pkg}.{m}" for m in PROTECTED):
        if start not in graph:
            continue
        seen, stack = set(), [(start, [])]
        while stack:
            mod, chain = stack.pop()
            if mod in seen:
                continue
            seen.add(mod)
            for name, line in graph.get(mod, ()):
                here = chain + [f"{files[mod].name}:{line}"]
                if forbidden(name):
                    v.append(f"{files[start]}:{here[0].split(':')[1]}: R1 {start} reaches model client "
                             f"'{name}' via {' -> '.join(here)}")
                elif name in graph:
                    stack.append((name, here))

    # R2 / R3 — per-file AST scan
    for mod, tree in trees.items():
        fname = files[mod].name
        for n in ast.walk(tree):
            if fname != "confirmation.py":
                if isinstance(n, ast.Call) and (
                        (isinstance(n.func, ast.Name) and n.func.id == "ConfirmationReceipt") or
                        (isinstance(n.func, ast.Attribute) and n.func.attr == "ConfirmationReceipt")):
                    v.append(f"{files[mod]}:{n.lineno}: R2 ConfirmationReceipt constructed outside confirmation.py")
                if (isinstance(n, ast.Name) and n.id == "_SENTINEL") or \
                        (isinstance(n, ast.Attribute) and n.attr == "_SENTINEL") or \
                        (isinstance(n, ast.alias) and n.name == "_SENTINEL"):
                    v.append(f"{files[mod]}:{getattr(n, 'lineno', 0)}: R2 receipt sentinel referenced outside confirmation.py")
            if fname != "form_state.py" and isinstance(n, ast.Attribute) and n.attr == "_values":
                v.append(f"{files[mod]}:{n.lineno}: R3 FormState._values accessed outside form_state.py")
            if fname != "form_state.py" and isinstance(n, ast.Constant) and n.value == "_values":
                v.append(f"{files[mod]}:{n.lineno}: R3 '_values' used via reflection outside form_state.py")
    return sorted(set(v))
