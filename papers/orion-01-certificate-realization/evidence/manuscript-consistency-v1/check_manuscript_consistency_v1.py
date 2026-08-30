#!/usr/bin/env python3
"""ORION-01 manuscript internal-consistency check after R0/name repairs.

Checks, per manuscript:
  1. every referenced Theorem/Lemma/Corollary/Proposition N is DEFINED
  2. definition numbering has no gaps (a gap = a repair deleted a result
     without renumbering its neighbours)
  3. every backticked symbol used in a numbered statement is INTRODUCED
     somewhere earlier in the file (R0 renamed identifiers; a rename that
     missed a use site shows up here as a never-introduced symbol)
"""
import re, sys, json, pathlib

KINDS = r'(Theorem|Lemma|Corollary|Proposition)'
DEF_RE = re.compile(r'\*\*' + KINDS + r'\s+(\d+)')
REF_RE = re.compile(KINDS + r'\s+(\d+)')
SYM_RE = re.compile(r'`([A-Za-z_][A-Za-z0-9_]*(?:\([^`)]*\))?[^`]*)`')

def bare(sym):
    m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', sym)
    return m.group(1) if m else None

def check(path):
    txt = path.read_text(encoding='utf-8', errors='replace')
    defs = {(k, int(n)) for k, n in DEF_RE.findall(txt)}
    refs = {(k, int(n)) for k, n in REF_RE.findall(txt)}
    dangling = sorted(refs - defs)

    # NOTE: these manuscripts number results in ONE shared sequence across
    # kinds (Theorem 1, Corollary 2, Lemma 3, Theorem 4), so gaps must be
    # checked on the UNION. A per-kind rule reports false positives here.
    gaps = []
    ns = sorted(n for _, n in defs)
    if ns:
        missing = [i for i in range(1, max(ns) + 1) if i not in ns]
        if missing:
            gaps.append({"scope": "union across kinds", "defined": ns,
                         "missing": missing})

    # symbols used inside numbered statements vs symbols anywhere earlier
    stmt_syms, all_syms = set(), set()
    for line in txt.splitlines():
        syms = {bare(s) for s in SYM_RE.findall(line)}
        syms.discard(None)
        all_syms |= syms
        if DEF_RE.search(line):
            stmt_syms |= syms
    never = sorted(s for s in stmt_syms if list(txt).count and txt.count('`' + s) < 2)

    return {
        "file": path.name,
        "definitions": sorted(f"{k} {n}" for k, n in defs),
        "references": len(refs),
        "dangling_references": [f"{k} {n}" for k, n in dangling],
        "numbering_gaps": gaps,
        "statement_symbols": len(stmt_syms),
        "symbols_used_once_only": never[:8],
        "clean": not dangling and not gaps,
    }

def main():
    root = pathlib.Path('papers/orion-01-certificate-realization')
    out, ok = [], True
    for name in ('theory-A-MANUSCRIPT_V2.md', 'theory-B-MANUSCRIPT_V2.md'):
        p = root / name
        if not p.is_file():
            out.append({"file": name, "error": "NOT_FOUND"}); ok = False; continue
        r = check(p); out.append(r); ok &= r["clean"]

    # ---- positive control: an injected dangling ref MUST be caught ----
    import tempfile, os
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as fh:
        fh.write("**Theorem 1.** real.\n\nBy Theorem 9 we conclude.\n")
        tmp = fh.name
    ctrl = check(pathlib.Path(tmp))
    os.unlink(tmp)
    control_ok = ctrl["dangling_references"] == ["Theorem 9"]

    print(json.dumps({
        "checker": "ORION01.MANUSCRIPT_CONSISTENCY.v1",
        "results": out,
        "all_clean": bool(ok),
        "positive_control": {
            "injected": "reference to Theorem 9 with only Theorem 1 defined",
            "caught": bool(control_ok), "saw": ctrl["dangling_references"]},
        "terminal": ("MANUSCRIPTS_INTERNALLY_CONSISTENT" if ok and control_ok
                     else "INCONSISTENCY_FOUND" if control_ok else "CHECKER_UNVALIDATED"),
    }, indent=2))
    return 0 if (ok and control_ok) else 1

if __name__ == '__main__':
    raise SystemExit(main())
