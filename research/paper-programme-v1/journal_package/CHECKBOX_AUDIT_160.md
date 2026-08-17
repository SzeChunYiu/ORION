# Issue #160 checkbox audit versus `origin/main`

Frozen at subject `b7cfaecfb55d9ad6c12fb59374935769ed8d8787`. This ticks **verified** Gate 7–9 inventory items. Unticked items stay `CANNOT_CHECK` or `OPEN`. Scientific verification records are owned by #283 and are not duplicated here.

Parents: #153, #97. Child paper issues: #98 CLOSED, #99 OPEN, #100 OPEN, #101 CLOSED, #102 OPEN.

## Gate 7 — reproducible artifact

| Item | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Frozen source/result identity | [x] suite/archive bound in T2 provenance | [x] offline record digest | [x] confirmatory gold/exec freeze | [x] subject `f6e51b5c…` + campaign `31976589735` | [x] attribution report bound to suite path |
| Dependency/environment lock | [ ] no lockfile beyond `pyproject.toml` | [ ] same | [ ] same | [ ] same | [ ] same |
| Clean-machine install test | [ ] | [ ] | [ ] | [ ] | [ ] |
| Headline reproduction path | [x] `make paper01-results` | [x] offline summary + claim-ledger checker | [x] `make paper03-public-reference-publication` | [x] `generate_figures.py` + independent reproduce | [x] `REPRODUCE.md` freeze path |
| Raw manifests/logs/evaluator decisions | [x] `results/raw/` | [x] offline + MetaSyn/Deep archives | [x] confirmatory evidence dir | [x] safe V2 aggregates; protected gold withheld | [x] attribution `results.jsonl` |
| Seeds/settings | [x] protocol statistics | [x] offline freeze | [x] execution manifest | [x] binding manifest V2 | [x] protocol V1/V2 |
| Scripts for figures/tables | [x] `orion.study.p1.tables` | [x] P2 render/check scripts | [x] publication generator | [x] `figures/generate_figures.py` | [ ] P5-2..P5-7 need a result archive |
| Runtime/hardware/cost | [ ] | [x] MetaSyn wall-clock only | [ ] | [x] campaign telemetry | [ ] |
| Licenses/restrictions | [ ] root LICENSE missing | [ ] same; third-party noted | [ ] same | [ ] same; protected gold excluded | [ ] same |
| Permanent archive/DOI | [ ] | [ ] | [ ] | [x] GitHub Release tag; [ ] DOI | [ ] |
| Independent reproduction | [ ] | [ ] | [x] confirmatory replay path | [x] independent receipt | [ ] |

## Gate 9 — journal submission package

| Item | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Target journal / recent-article scope | [ ] | [x] `JOURNAL_SCOPE_CHECK.md` (TMLR; contingent) | [ ] | [x] TMLR checklist | [ ] |
| Journal template/style/length | [ ] article class draft | [ ] not TMLR | [ ] article class draft | [x] TMLR source; [ ] in-tree PDF | [ ] |
| Cover letter | [ ] | [x] draft only | [ ] | [x] `COVER_NOTE_TMLR.md` | [ ] |
| Funding/conflicts/contributions | [ ] | [ ] | [ ] | [x] anonymous TMLR block | [ ] |
| Data/code availability wording | [x] §09 | [x] availability section | [ ] incomplete | [x] result-bound | [x] `REPRODUCE.md` |
| Reference/DOI metadata audit | [ ] | [ ] blocked on compile | [ ] | [x] TMLR audit workflow | [ ] |
| Print/grayscale figures | [ ] | [ ] | [x] SVG publication set | [x] generated from aggregates | [ ] |
| Independent final PDF proofread | [ ] OPEN | [ ] OPEN | [ ] OPEN | [ ] OPEN in-tree (release PDF remote) | [ ] OPEN |

## Claim-ledger / PDF audit (this package)

- [x] P1 H1 remains **NOT_SUPPORTED** against `P1-T2`.
- [x] Every paper lists claims vs artifacts; PDF proofread is **OPEN** where no in-tree PDF exists.
- [x] Missing required package files fail `check_journal_package.py`.
- [x] Consumes issue #283 `orion.scientific-result-verification.v1` records under `research/verification/records/`.

## Terminal

Issue #160 cannot close: packages are `SCAFFOLDING`, #99/#100/#102 remain open, and in-tree PDFs are absent. P4's declared `PEER_REVIEW_READY` is recorded, not re-litigated.
