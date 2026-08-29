# Adoption of the codex top-tier lane

Three codex branches adopted, one held back. All were checked with
`check_branch_adoption_safety_v1.py` before merging.

## Adopted (78 files, purely additive)

| branch | files | classification | evidence losses |
|---|---:|---|---:|
| `codex/all25-top-tier-gap-closure-20260829-pro` | 28 | 100% `ONLY_ON_BRANCH` | **0** |
| `codex/top-tier-science-closure-v3-20260829` | 21 | 100% `ONLY_ON_BRANCH` | **0** |
| `codex/issue-1729-all25-atomic-gap-ledger-v2-20260829` | 29 | 100% `ONLY_ON_BRANCH` | **0** |

Verified on the merged tree: **0 deletions, 0 modifications to existing files.** Nothing
already on `main` is touched.

## Held back, and why

`codex/all25-science-gap-spine-20260829` (2026-08-29 11:04) conflicts on all 21 of its
files with `…-pro` (12:13). It is **not** cleanly superseded — the two diverged:

| file | in adopted set | in spine |
|---|---:|---:|
| `README.md` | 3,914 B | 1,919 B |
| `LATEST_MAIN_SCIENCE_AUDIT_2026-08-29.md` | 4,464 B | 2,839 B |
| `finite_information_interface_v1/RESULT.json` | 678 B | **767 B** |
| `finite_information_interface_v1/THEORY.md` | 7,433 B | **10,519 B** |

The adopted set carries the fuller audit; the spine carries the fuller **theory**.
Force-merging in either direction discards real content, so it is left for per-file
reconciliation rather than resolved by picking a side. `THEORY.md` and `RESULT.json` are
where the spine has more to give.

## Why this lane matters

The atomic gap ledger (`TOP_TIER_ATOMIC_GAP_LEDGER_V2`) supplies what was otherwise being
rebuilt by hand: seven named journal submission gates and a four-wave execution order over
all 25 papers, with per-paper files and open-PR collision guards. It is correctly scoped —
`scientific_authority_delta: NONE`, `DRAFT_PRE_FREEZE_EXECUTION_MAP`, and an explicit
statement that no row is a preregistration or terminal by itself.

Work completed independently in this session lands inside its structure, which is
corroboration rather than coincidence:

| ledger gate / wave | independently completed work |
|---|---|
| **J2_NEAREST_WORK** — "submission-date refresh" | ORION-08 literature closure found arXiv:2608.25553v2 (2026-08-27) and reopened the gate |
| **J5_INDEPENDENT_AUTHORITY** — "independent proof/replay" | ORION-08 `REPLAY_EXACT` 3/3; ORION-06 and ORION-09 replays 2/2 each |
| **W0_INTEGRITY_AND_CANONICALIZATION** — ORION-02/11/17/19 | ORION-11 corpus-leakage repair; ORION-17 disagreement study → `NO_DISCRIMINATION` |
| **W1_EXACT_THEORY_AND_INSTRUMENT_AUTHORITY** — ORION-01/04/05/09/10/20 | ORION-05 complexity-1 census complete (33,755/33,755 `OK`); ORION-09 replay gate closed |

Two independent lanes converging on the same gate structure and the same wave assignment
is worth more than either derivation alone.
