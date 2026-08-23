# P1-P15 mechanical, render and harness audit

Date: 2026-08-22

## Scope and authority

Manuscript candidate: `cdea6eb85033e85e41e50242f44e28f6b9a0e423`.
Harness candidate: `914927cd7ae14c52af8b4b8b132ae83823d12be2`.

This report establishes mechanical facts only. It grants no scientific,
novelty, publication-readiness or global-stop authority.

## Answer-free dual source audit

Two independent deterministic implementations scanned the candidate manuscript
bytes. Neither lane invokes an LLM or a host-completed capability.

- terminal: `P1_P15_DUAL_SOURCE_AUDIT_AGREEMENT`;
- source digest: `sha256:420206d72f0c1910b55642ff417fde902a24c1e3bcc8706d62a67747d99dfcb4`;
- Lane A LLM calls: `0`;
- Lane B LLM calls: `0`;
- disagreements: `0`;
- hostile disagreement test: pass;
- unit suite: `4 passed`.

The agreement supports only source-tree facts. It does not adjudicate manuscript
truth or novelty.

## Chapter-source audit

| Paper | Status | Chapter TeX | Self-contained TeX | Markdown runtime wrappers | Branding hits | Placeholders |
|---|---|---:|---:|---:|---:|---:|
| P1 | structural review | 14 | 14 | 0 | 2 | 0 |
| P2 | structural review | 7 | 7 | 0 | 2 | 0 |
| P3 | structural review | 13 | 13 | 0 | 8 | 0 |
| P4 | structural review | 11 | 11 | 0 | 2 | 0 |
| P5 | blocked | 12 | 12 | 0 | 3 | 1 |
| P6 | structural review | 8 | 8 | 0 | 0 | 0 |
| P7 | structural review | 7 | 7 | 0 | 0 | 0 |
| P8 | structural review | 10 | 10 | 0 | 1 | 0 |
| P9 | structural review | 8 | 8 | 0 | 0 | 0 |
| P10 | structural review | 16 | 16 | 0 | 15 | 0 |
| P11 | blocked | 10 | 0 | 10 | 2 | 0 |
| P12 | blocked | 10 | 0 | 10 | 1 | 0 |
| P13 | blocked | 10 | 0 | 10 | 1 | 0 |
| P14 | blocked | 9 | 0 | 9 | 15 | 0 |
| P15 | incomplete | 0 | 0 | 0 | 0 | 0 |

P11-P14 have `.tex` files per chapter, but each is only a `\markdownInput`
wrapper. The scientific text remains in Markdown and the clean build requires a
runtime Markdown TeX stack. That is not the requested self-contained chapter-TeX
submission surface.

P5's live placeholder is
`manuscript/sections/10-limitations.tex:13`.

## Clean LaTeX build

Command per paper:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

| Paper | Result | Pages | Final unresolved citations/references | Final overfull boxes |
|---|---|---:|---:|---:|
| P1 | pass | 30 | 0 | 0 |
| P2 | pass | 27 | 0 | 0 |
| P3 | pass | 21 | 0 | 0 |
| P4 | pass | 15 | 0 | 0 |
| P5 | pass | 16 | 0 | 0 |
| P6 | pass | 6 | 0 | 0 |
| P7 | pass | 6 | 0 | 0 |
| P8 | pass | 9 | 0 | 0 |
| P9 | pass | 9 | 0 | 0 |
| P10 | pass | 7 | 0 | 4 |
| P11 | direct build fails; repository `make` passes in complete toolchain | 8 | not yet portable-audited | not yet portable-audited |
| P12 | direct build fails; repository `make` passes in complete toolchain | 6 | not yet portable-audited | not yet portable-audited |
| P13 | direct build fails; repository `make` passes in complete toolchain | 5 | not yet portable-audited | not yet portable-audited |
| P14 | direct build fails; repository `make` passes in complete toolchain | 6 | not yet portable-audited | not yet portable-audited |
| P15 | no manuscript | n/a | n/a | n/a |

P11-P14 expose an environment-underbinding defect rather than an absolute build
failure. In the primary clean environment, direct `latexmk` fails before content
rendering because `markdown.sty` requires `gobble.sty`, which is absent. A mutually
blind reviewer independently built all four through each repository `Makefile`,
which enables `-shell-escape`, in a more complete TeX environment. The two results
are compatible: the special repository build path can succeed, while an ordinary
direct-LaTeX submission build is not portable or self-contained. The shared
finding was placed on PR #831 as a cross-agent verification note. The preferred
repair is tracked, self-contained TeX chapters. If runtime Markdown conversion is
intentional, the package must instead pin the complete toolchain, declare the
shell-escape trust boundary, start from a clean generated-state directory, and
prove source-to-PDF text equivalence.

## Visual PDF inspection

First, middle and final pages of every cleanly built P1-P10 PDF were rendered to
images and inspected.

- P1-P3 and P5 visibly identify themselves as `Working framework draft`.
- P6-P8 visibly retain internal version, release-overlay, receipt and working-draft
  material. This is an audit package, not a neutral journal manuscript surface.
- P9 is the closest to a conventional anonymous submission surface.
- P10 uses a verified-superiority title and internal P10/ORION programme language
  while its result remains prospective. Four overfull boxes remain.
- No sampled page showed clipped text, broken glyphs or overlapping figures, but
  sampled-page inspection is not a substitute for a final page-by-page audit after
  scientific repairs.

## Bibliographic surface

The current bibliography counts are:

| Paper | Entries | Entries with DOI | Entries with URL |
|---|---:|---:|---:|
| P1 | 42 | 8 | 0 |
| P2 | 46 | 15 | 26 |
| P3 | 26 | 18 | 2 |
| P4 | 20 | 1 | 1 |
| P5 | 16 | 0 | 0 |
| P6 | 14 | 4 | 0 |
| P7 | 14 | 2 | 0 |
| P8 | 13 | 3 | 0 |
| P9 | 16 | 15 | 0 |
| P10 | 4 | 0 | 0 |
| P11 | 3 | 0 | 0 |
| P12 | 2 | 0 | 0 |
| P13 | 2 | 0 | 0 |
| P14 | 2 | 0 | 0 |
| P15 | 0 | 0 | 0 |

Counts do not prove support or metadata validity. P10-P15 are visibly below a
defensible literature-review surface for their current breadth. Every central
claim still needs claim-local primary-source verification and contradictory or
limiting evidence screening.

## Harness isolation verification

On the isolated PR #871 archive:

- `25 passed` across paper-contract, P1-P15 programme, research-director and V4
  outcome-lifecycle tests;
- `12 passed` across dual-consensus, runtime CLI and execution-coverage tests;
- all four documented operational terminals were emitted;
- every terminal explicitly denies scientific, novelty, promotion and global-stop
  authority.

This establishes executable conformance for the tested contracts. It does not
establish that the dual proposer lanes are independent.

### Independence blocker

`paper_structure_consensus.py` names `lane_a` and `lane_b` but sends both through
the same `BrokerLLMProvider`. The broker accepts optional model metadata, yet the
consensus merge does not bind or compare executor, provider or model-family
identity. One host/model can therefore answer both requests and satisfy agreement.
Exact source-span checks prevent unsupported quotations; they do not prove lane
independence or that the harness, rather than one model, supplied the semantic
judgment.

The cross-agent note on PR #871 requests a fail-closed independence predicate:
bind executor/provider/model-family/request/epoch identities, require distinct
admissible lanes, and emit `CANNOT_CHECK_INDEPENDENCE` for missing or same-family
identity. Until that closes, the accurate term is **two-request consensus**, not
independent-lane consensus.

## Negative-result rule

A negative result must never be edited into a positive observation. It can yield
a positive scientific contribution only by supporting a bounded obstruction,
sharp boundary, falsified generalization, mechanism diagnosis or prospectively
frozen successor. Repair verification and fresh scientific evaluation must remain
separate. If no honest positive successor exists, the negative remains part of the
paper or the claimed paper identity is narrowed.

## Additive P15 repair on this branch

Because the candidate manuscript lane contains no P15 manuscript bytes, this
branch adds a non-overlapping framework manuscript without rewriting the active
P1-P14 lane:

- neutral title: *Fail-Closed Research Execution: Receipt Semantics and
  Independence Contracts*;
- `main.tex` plus 10 complete, tracked chapter TeX files;
- 13 bibliography entries with claim-local citations and no missing keys;
- zero manuscript branding, codebase references or placeholder hits;
- a claim ledger whose status is
  `FRAMEWORK_COMPLETE / NO_PROTECTED_PAPER_RESULT`;
- clean direct build without shell escape: 10 pages, no unresolved references,
  no overfull/underfull warnings;
- PDF SHA-256:
  `ee2c034a556b73034d9f2dda0ecb8668f49710a26d83d0a245addf09e4195691`;
- visual inspection of the first, middle and final pages found no clipping,
  overlap or broken glyphs.

The corrected dual source scanner recognizes both `sections/` and `chapters/` as
canonical chapter roots. Its five-test suite passes. On this branch both lanes
report 10 P15 chapter files, zero model calls and zero disagreements under source
digest
`sha256:92ce14549317062c7af7fbdb0658b188e263a94e52f50a7d42216a95ad28508b`.
This remains structural conformance, not publication or scientific authority.
