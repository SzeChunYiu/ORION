#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / 'papers/orion-12-open-world-scientific-discovery/manuscript/ipm_submission.tex'
OUTDIR = ROOT / 'build/orion12_release'
OUT = OUTDIR / 'arxiv.tex'
def fail(msg): print('ORION12_ARXIV_BUILD=FAIL\n- '+msg); return 1
def main():
    text = SRC.read_text(encoding='utf-8')
    replacements = {
        'pdfauthor={Anonymous authors}': 'pdfauthor={Sze Chun Yiu}',
        r'\author[1]{Anonymous authors}': r'\author[1]{Sze Chun Yiu}\ead{sze-chun.yiu@fysik.su.se}',
        r'\shortauthors{Anonymous authors}': r'\shortauthors{Sze Chun Yiu}',
    }
    for old,new in replacements.items():
        if old not in text: return fail('missing source token: '+old)
        text = text.replace(old,new)
    old_ai = r'''\section*{Declaration of generative AI and AI-assisted technologies}

During preparation of this work, the authors used OpenAI ChatGPT to support
literature searching, source checking, reproducibility review, manuscript
editing, and submission-package preparation. The tool was not treated as an
author and did not replace scientific judgment. Result-bearing statements and
citations were checked against the archived evidence and primary-source
records. The authors remain responsible for the article's content.
'''
    new_ai = r'''\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}
During the preparation of this work, the author used OpenAI ChatGPT and related language-model tooling to support literature triage, source checking, reproducibility review, code and manuscript auditing, organization, and language refinement. The author reviewed and edited all AI-assisted output, checked the scientific claims and cited sources against the underlying evidence, and takes full responsibility for the content of the article.

\section*{Funding}
The author received no specific funding for this work.

\section*{Competing interests}
The author declares no competing interests.
'''
    if old_ai not in text: return fail('AI declaration block missing')
    text = text.replace(old_ai,new_ai)
    for token in ('Sze Chun Yiu','sze-chun.yiu@fysik.su.se','The author received no specific funding','The author declares no competing interests','TREC-COVID'):
        if token not in text: return fail('required token missing: '+token)
    if 'Anonymous authors' in text: return fail('anonymous metadata remains')
    OUTDIR.mkdir(parents=True,exist_ok=True); OUT.write_text(text,encoding='utf-8')
    print('ORION12_ARXIV_BUILD=PASS'); print('OUTPUT='+str(OUT)); return 0
if __name__=='__main__': sys.exit(main())
