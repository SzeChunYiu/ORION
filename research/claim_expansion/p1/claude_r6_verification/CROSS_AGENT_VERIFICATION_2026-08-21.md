# Cross-agent verification note (Claude lane) — P1-U R6 native primary

**Date:** 2026-08-21
**Observing lane:** `claude/papers-1-10-issues-uqrj2o`
**Subject:** `codex/p1-r6-current-main-fix-20260821` (PR #732), `codex/p1-r6-diagnostic-20260821` (PR #730)
**Method:** read-only. `git archive` of the subject refs into a scratch tree, private venv,
per the `AGENTS.md` verification rule. `/home/user/ORION` was never used to run subject code.

**Authority:** none. This note is a verification observation about another lane's in-flight
work. It scores no terminal, promotes no claim, and is **not** recorded as evidence against
any `P1-U` gate in
`research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`. Doing so would be
the post-hoc promotion `HC-SUP-POST-HOC-FREEZE` exists to refuse.

## 1. The digest defect was the only thing between R6 and a scored primary

Confirmed independently by three verification passes, each running the real 48-episode
pipeline against the frozen R5 corpus:

| | unpatched `gpt_r6_native_primary.py` | via `gpt_r6_native_primary_schema_fix.py` |
| --- | --- | --- |
| `native_invalid_rows` | 48 / 48 | 0 |
| `every_native_row_bound` | `False` | `True` |
| every other check | already `True` | `True` |
| terminal | `P1_R6_PRIMARY_NOT_SUPPORTED` | `P1_R6_PRIMARY_PASS_PENDING_2019_REPLICATION` |

So the campaign was one representation mismatch away from a scored result, and every other
engineering gate was already green underneath it. That is the positive finding: **P1 is not
stuck for want of evidence.**

The defect is broader than first diagnosed. All **five** per-arm digest fields are canonical,
not only the assessment digests — `revision_gate_digest` reaches the row from
`orion.self_orion.revision_gate`, a different subsystem, which also imports `content_digest`
from `orion.transfer.v2.canonical`.

## 2. Three findings that survive a green run

These are ordered by what they cost. The first is the one that matters.

### 2.1 The ablation arm is inert, so the gain is not attributable — `MEASUREMENT_OR_EVALUATOR`

`ORION_NATIVE_BASE` returns `UNRESOLVED` on **48/48 episodes**. The solver never reaches
`DIAGNOSE` — observed operator sequences across all 48 rows contain only
`RECURSE/FRAME/SEARCH/ABSORB/RECONSTRUCT/DETECT/SATURATE_BOUNDED` — so `diagnosis_token` is
`None` throughout, `_base_responsibility` receives `observed={}`, and both responsibility and
gate resolve to `UNRESOLVED`.

Issue #723 adds the BASE arm for one reason: to show that any gain comes from the native ARD
addition **rather than merely from runtime wrapping**. Against a constant arm that question
cannot be answered. All six families "differ from BASE" trivially.

Compounding it, the disjunction in that requirement is only half implemented. "Behaviorally
differ" is operationalized as `ard.choice != base.choice` on the adverse member, bucketed by
class and checked for non-emptiness — no count, no threshold, no direction, so one differing
episode passes even if ARD is worse. "Materially outperform" is **not computed anywhere**:
there is no per-family ARD-vs-BASE margin and no CI, since the bootstrap is only ever applied
to ARD−B3.

**Until the BASE arm reaches `DIAGNOSE`, the R6 primary cannot support a P1-U superiority
claim however large the ARD−B3 margin is.**

### 2.2 Two guards do not test what they are named — `MEASUREMENT_OR_EVALUATOR`

- **Class noninferiority never sees the control class.** Both members of every pair are filed
  under `adverse_class`, because the accumulation sits inside the
  `for member in ("adverse", "control")` loop. There is therefore no
  `NO_HIGH_LEVEL_REFORMULATION` stratum at all — the matched-control gold class, which is the
  entire point of the control condition, is never evaluated for noninferiority.
- **Domain noninferiority has no margin.** Every pair has a unique `actual_domain`, giving 26
  strata of 1–2 episodes. The smallest attainable negative stratum mean is −0.5, so the −0.10
  "noninferiority margin" is in fact a hard *ARD may never lose a single episode* rule.

### 2.3 "Protected adverse family" does not exist as a label — `MEASUREMENT_OR_EVALUATOR`

The phrase appears in #723 and in a check name. The code substitutes `adverse_class`, i.e. the
gold label being predicted. Nothing on the branch can currently distinguish a family-level
mechanism claim from a per-class scoring artifact.

## 3. Engineering findings

- **The repair is an overlay.** `gpt_r6_native_primary.py` still applies raw-hex64 to canonical
  digests; only the sibling `schema_fix` module installs the corrected validator, and only the
  CI workflow calls it. Running the primary directly — the obvious command — still yields
  48/48 invalid rows and `P1_R6_PRIMARY_NOT_SUPPORTED`, silently. No test anywhere imports
  either module.
- **The wrapper is not idempotent.** `_ORIGINAL_NATIVE_ROW_VALID` is resolved at call time, so a
  double installation (run as `__main__` plus a normal import, a `reload`, or a second lane
  installing its own copy) captures the already-patched wrapper. It does not recurse — because
  the second-level digests are already raw, so normalization returns `None` and it returns
  `False` first. The "recursion-safe" property therefore holds by accident, and the price is
  worse than a crash: 100% of valid rows silently rejected again.
- **`--self-test` cannot detect adapter drift.** It validates a hand-written fixture; with
  `run_native_episode` disabled entirely it still prints `PASS`. If any producer reverted to a
  raw digest the primary would return to 48/48 rejected while the CI step named "Prove
  digest-schema repair is fail-closed" still reported `PASS`.
- **A 192-mutant differential fuzz found no acceptance widening.** Every divergence between the
  wrapper and an independently written both-schema validator is fail-closed. One pre-existing
  weakness is preserved rather than introduced: `str(value)` coercion accepts a non-`str`
  object whose `__str__` renders as a digest.
- **The 2019 replication cannot run through this evaluator.** `source_year == 2020`, the exact
  retained-failure list `["MEAS-P2", "BOUND-P1"]`, and `n_episodes == 48` are hard-wired. A
  2019 corpus identical in every other respect returns `P1_R6_CANNOT_CHECK_FIXED_DATA` with
  zero episodes executed and **no exception raised** — the same shape of false negative as the
  digest defect. No 2019 corpus, builder or protocol exists on the branch.
- **The frozen inputs live on one deletable ref.** `--builder` and `--fixed` exist only at
  commit `ab5a1d4937c884a975c90f90fc619964cd740582`, reachable from exactly one ref:
  `refs/remotes/origin/shadow/p1-u-gpt-r6-native-runtime-20260820`. Delete or GC that branch
  and R6 becomes unreproducible.
- **Leakage checking is weaker than its name.** `_leakage_free` is fail-open on a missing
  `request_payloads` key; pair role is not a forbidden token (covered only incidentally,
  because the episode id embeds `-A`/`-C`/`-U`); and the row keeps only
  `request_payload_digest`, so leakage cannot be re-audited from the artifact with a corrected
  token set. Order is correct: the check runs before the payloads are popped.
- **Artifacts are not byte-comparable across runs.** Two identical runs differ in
  `runtime.trace_id` and `runtime.receipt_ids`. Every scored field and digest is identical.

## 4. What this changes for #649

The P1 blocker is no longer "the primary cannot produce rows". It is:

1. make the digest repair durable rather than an overlay — the representation vocabulary is in
   `src/orion/core/digests.py`, and the repair belongs in `_native_row_valid` itself;
2. **give the BASE arm a reachable `DIAGNOSE` path**, without which no R6 outcome is
   attributable to the ARD mechanism;
3. repair the two mis-specified guards and define "protected adverse family" as a real label;
4. parameterize the year, retained-route list and episode count so the 2019 replication can
   run at all, and build that corpus;
5. tag or vendor the frozen 2020 inputs.

Items 2 and 3 are pre-outcome protocol repairs. Under the R4 precedent
(`PRE_OUTCOME_PROTOCOL_REPAIR__NO_RESULT_AUTHORITY`) they may be made without touching the
frozen source universe, provided they land before the outcome is read as a P1-U result.
