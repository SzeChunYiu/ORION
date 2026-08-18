#!/usr/bin/env python3
"""Render/check legible publication TikZ variants of P2-3 and P2-4.

The scientific coordinates and authority remain owned by
``render_offline_mechanisms.py`` and ``OFFLINE_MECHANISMS_V1.json``.  This module
imports the canonical renderer and changes only annotation layout so the compiled
journal PDF has no overlapping axis/header, short-bar labels, or clipped scope
annotations.  The figure captions retain the full claim/authority boundary.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "render_offline_mechanisms.py"
PAPER = HERE.parent
FIGURES = PAPER / "manuscript" / "figures"
SOURCE = PAPER / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json"


def _base():
    spec = importlib.util.spec_from_file_location("orion_p2_mechanism_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical offline mechanism renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _p3(text: str) -> str:
    """Move the P2-3 y-axis title; leave evidence-derived scope text untouched."""
    old = r"\draw[->] (0,0) -- (0,1.08) node[above]{complete-gold recall};"
    new = "\n".join(
        [
            r"\draw[->] (0,0) -- (0,1.08);",
            r"\node[rotate=90,anchor=south] at (-0.62,0.54) {complete-gold recall};",
        ]
    )
    if old not in text:
        raise ValueError("canonical P2-3 y-axis token missing")
    return text.replace(old, new)


def _p4(text: str) -> str:
    """Move P2-4 annotations for legibility without changing scientific values."""
    old_axis = r"\draw[->] (0,0) -- (0,3.45) node[above]{mean first relevant contribution};"
    new_axis = "\n".join(
        [
            r"\draw[->] (0,0) -- (0,3.45);",
            r"\node[rotate=90,anchor=south] at (-0.48,1.72) {mean first relevant contribution};",
        ]
    )
    if old_axis not in text:
        raise ValueError("canonical P2-4 y-axis token missing")
    text = text.replace(old_axis, new_axis)

    replacements = {
        r"\node[rotate=90,anchor=west,font=\scriptsize] at (0.7,0.10) {reference};":
            r"\node[font=\tiny,text=white] at (0.7,1.50) {ref.};",
        r"\node[rotate=90,anchor=west,font=\scriptsize] at (1.7,0.10) {independent};":
            r"\node[font=\tiny,text=white] at (1.7,1.00) {ind.};",
        r"\node[rotate=90,anchor=west,font=\scriptsize] at (2.7,0.10) {independent};":
            r"\node[font=\tiny,text=white] at (2.7,1.00) {ind.};",
        r"\node[rotate=90,anchor=west,font=\scriptsize] at (3.7,0.10) {shared backend};":
            r"\node[font=\tiny,text=black] at (3.7,0.46) {shared};",
        r"\node[rotate=90,anchor=west,font=\scriptsize] at (4.7,0.10) {independent};":
            r"\node[font=\tiny,text=white] at (4.7,0.43) {ind.};",
    }
    for old, new in replacements.items():
        if old not in text:
            raise ValueError(f"canonical P2-4 layout token missing: {old}")
        text = text.replace(old, new)

    scope_prefix = r"\node[anchor=west,font=\small] at (0,3.70) {"
    scope_line = next(
        (line for line in text.splitlines() if line.startswith(scope_prefix)),
        None,
    )
    if scope_line is None:
        raise ValueError("canonical P2-4 scope token missing")
    n_tasks = scope_line[len(scope_prefix):].split(" frozen tasks;", 1)[0]
    if not n_tasks.isdigit():
        raise ValueError("canonical P2-4 scope does not start with a task count")
    compact_scope = (
        rf"\node[anchor=west,font=\scriptsize,text width=7.2cm,align=left] at (0,3.70) "
        rf"{{{n_tasks} frozen tasks; content-identity contribution; descriptive only}};"
    )
    return text.replace(scope_line, compact_scope)


def render() -> dict[Path, str]:
    base = _base()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    base._validate(data)
    return {
        FIGURES / "P2-3_cumulative_discovery_publication.tex": _p3(base.render_p2_3_tex(data)),
        FIGURES / "P2-4_route_contribution_publication.tex": _p4(base.render_p2_4_tex(data)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = render()
    if args.check:
        mismatches = []
        for path, expected in outputs.items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                mismatches.append(str(path))
        if mismatches:
            raise SystemExit("publication mechanism layout drift: " + ", ".join(mismatches))
        print("publication mechanism layouts match canonical coordinates and legibility transform")
        return 0
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
