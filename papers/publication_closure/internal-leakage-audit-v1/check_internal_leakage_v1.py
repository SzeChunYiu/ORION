#!/usr/bin/env python3
"""Fail-closed audit for internal identifiers leaking into manuscript surfaces.

Author rule: no version numbers, internal labels, or project codes anywhere in a
paper. Those are internal bookkeeping and must not reach a referee.

Classes detected, in descending severity:
  TITLE_VERSION   a version tag in \title{} (a referee sees this first)
  TITLE_CODE      an internal project code in \title{}
  AUTHOR_CODE     an internal identifier in \author{}
  BODY_TERMINAL   a SCREAMING_SNAKE machine terminal in prose
  BODY_VERSION    a bare version tag (V1, V2, ...) used in prose
  BODY_PAPERCODE  an ORION-NN / P-NN project code in prose

Reports only; it repairs nothing. grants_authority: NONE.
"""
from __future__ import annotations
import json, pathlib, re, sys

VERSION   = re.compile(r'(?<![A-Za-z])V\d+(?![0-9A-Za-z])')
PAPERCODE = re.compile(r'\bORION[-_]?P?\d+\b|(?<![A-Za-z])P\d+[A-Z]?(?![0-9A-Za-z])')
TERMINAL  = re.compile(r'\b[A-Z][A-Z0-9]*_[A-Z0-9_]{3,}\b')
PROJCODE  = re.compile(r'\bORION[-_][A-Z]{2,}\b')

def field(text: str, name: str) -> str | None:
    m = re.search(r'\\' + name + r'\{(.+?)\}', text, re.S)
    return re.sub(r'\s+', ' ', m.group(1)) if m else None

def audit_paper(md: pathlib.Path) -> dict:
    main = md / 'main.tex'
    if not main.is_file():
        return {'status': 'NO_MAIN_TEX'}
    head = main.read_text(errors='replace')
    body = ''.join(f.read_text(errors='replace')
                   for f in sorted(md.glob('*.tex')) + sorted(md.glob('sections/*.tex')))
    title  = field(head, 'title') or ''
    author = field(head, 'author') or ''
    findings = {
        'TITLE_VERSION':  VERSION.findall(title),
        'TITLE_CODE':     PROJCODE.findall(title) + PAPERCODE.findall(title),
        'AUTHOR_CODE':    PROJCODE.findall(author) + PAPERCODE.findall(author),
        'BODY_TERMINAL':  sorted(set(TERMINAL.findall(body)))[:5],
        'BODY_VERSION':   VERSION.findall(body),
        'BODY_PAPERCODE': PAPERCODE.findall(body),
    }
    counts = {k: len(v) for k, v in findings.items()}
    return {
        'status': 'CLEAN' if not any(counts.values()) else 'LEAKAGE',
        'title': title[:90], 'author': author[:50],
        'counts': counts,
        'body_terminal_examples': findings['BODY_TERMINAL'],
    }

def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    out = {}
    for d in sorted((root / 'papers').glob('orion-*')):
        md = d / 'manuscript'
        if md.is_dir():
            out[d.name] = audit_paper(md)
    hard = {k: v for k, v in out.items()
            if v.get('counts', {}).get('TITLE_VERSION')
            or v.get('counts', {}).get('TITLE_CODE')
            or v.get('counts', {}).get('AUTHOR_CODE')}
    report = {
        'schema': 'ORION.INTERNAL_LEAKAGE_AUDIT.v1',
        'papers': out,
        'hard_violations_title_or_author': sorted(hard),
        'totals': {k: sum(v.get('counts', {}).get(k, 0) for v in out.values())
                   for k in ('TITLE_VERSION','TITLE_CODE','AUTHOR_CODE',
                             'BODY_VERSION','BODY_PAPERCODE','BODY_TERMINAL')},
        'grants_authority': 'NONE',
        'terminal': ('NO_TITLE_OR_AUTHOR_LEAKAGE' if not hard
                     else 'TITLE_OR_AUTHOR_LEAKAGE_PRESENT'),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if hard else 0

if __name__ == '__main__':
    raise SystemExit(main())
