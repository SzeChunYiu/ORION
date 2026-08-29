#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = ROOT / 'papers/orion-16-formal-epistemic-structures-and-mechanics/submission/AIJ_MANUSCRIPT.tex'
UPDATE = pathlib.Path(__file__).with_name('V3_SCIENCE_UPDATE.tex')
OUTDIR = ROOT / 'build/orion16_release'
OUT = OUTDIR / 'AIJ_MANUSCRIPT_CURRENT.tex'
AUTHOR_OLD = r'\author{Sze Chun Yiu\\Department of Physics, Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}'
AUTHOR_NEW = r'\author{SzeChunYiu\\Stockholm University, Stockholm, Sweden\\\texttt{sze-chun.yiu@fysik.su.se}}'
ABSTRACT = r'''\begin{abstract}
Scientific agents change more than propositional belief. Mature theory already supplies truth and dependency maintenance, incremental computation, typed effects, continuing authorization, provenance, workflow reproducibility, and execution-attestation certificates. We ask a narrower question: when such systems operate on scientifically certified state, can donor-native computational or operational validity remain unchanged while scientific admissibility changes because a load-bearing evidence, source-authority, claim-scope, or verification-epoch obligation has changed? The base contract proves root-inclusive repair safety, distinguishes support soundness from minimax minimality, separates preservation from revalidation, requires faithful footprints for history-aware commutation, and conserves hard obligations and non-escalating authority. A prospectively frozen certificate-semantics successor generalizes the typed-erasure separation over three bounded donor embeddings. A forgetful map preserves each donor's native validity, yet whenever it erases a non-inert scientific certificate coordinate it need not reflect scientific admissibility. When all scientific obligations are discharged, the enrichment reduces exactly to donor-native validity; an ideal donor product carrying the same scientific coordinates and predicate is extensionally equivalent. A frozen finite model evaluates 1,536 states and records zero donor-preservation violations, 96 typed-erasure separation witnesses spanning all four scientific coordinates, 96 conservative-reduction cases with zero violations, zero ideal-product mismatches, 96 certificate-revocation countermodels, and 24 donor-valid no-alarm cases; a second implementation independently reproduces all headline counts. The contribution is a bounded scientific-admissibility enrichment and conservative-extension/separation theorem family, not generic certification, provenance, authorization, or deployed-agent superiority.
\end{abstract}'''
DECL = r'''\section*{Data and code availability}
The formal checkers, frozen countermodels, claim ledgers, and reproduction instructions supporting the bounded theorem claims are maintained in the public ORION repository. The V3 finite-model checker and its independent audit are included in the bound research record. Public repository availability is reproducibility infrastructure, not independent scientific verification. No human-subject or animal data are used.

\section*{Funding}
The author received no specific funding for this work.

\section*{Competing interests}
The author declares no competing interests.

\begin{thebibliography}{99}'''
def fail(msg): print('ORION16_CURRENT_AIJ=FAIL\n- '+msg); return 1
def main():
    text = BASE.read_text(encoding='utf-8')
    if AUTHOR_OLD not in text: return fail('historical author line missing')
    text = text.replace(AUTHOR_OLD, AUTHOR_NEW, 1)
    pat = re.compile(r'\\begin\{abstract\}.*?\\end\{abstract\}', re.S)
    if len(pat.findall(text)) != 1: return fail('abstract block count')
    text = pat.sub(lambda _: ABSTRACT, text, count=1)
    marker = r'\section{Discussion and implications for AI systems}'
    if marker not in text: return fail('discussion marker missing')
    text = text.replace(marker, UPDATE.read_text(encoding='utf-8').strip()+'\n\n'+marker, 1)
    dpat = re.compile(r'\\section\*\{Data, code, and competing-interest statements\}.*?\\begin\{thebibliography\}\{99\}', re.S)
    if len(dpat.findall(text)) != 1: return fail('historical declaration block missing')
    text = dpat.sub(lambda _: DECL, text, count=1)
    for token in ('SzeChunYiu','Stockholm University, Stockholm, Sweden','1,536 states','96 typed-erasure separation witnesses','zero ideal-product mismatches','The author received no specific funding','The author declares no competing interests','Declaration of generative AI'):
        if token not in text: return fail('required token missing: '+token)
    for token in ('AUTHOR INPUT REQUIRED','CORRESPONDING AUTHOR INPUT REQUIRED','supplied through the journal submission interface after author confirmation'):
        if token in text: return fail('placeholder remains: '+token)
    OUTDIR.mkdir(parents=True, exist_ok=True); OUT.write_text(text, encoding='utf-8')
    print('ORION16_CURRENT_AIJ=PASS'); print('OUTPUT='+str(OUT)); return 0
if __name__ == '__main__': sys.exit(main())
