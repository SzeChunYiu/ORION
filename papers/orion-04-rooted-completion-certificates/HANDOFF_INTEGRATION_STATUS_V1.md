# ORION-04 — status of the exact-theorem handoff integration

**Date:** 2026-08-29
**Authority:** issue #1701 board, P0 line — *"ORION-04: integrate exact theorem handoff;
rerun checkers; map PR #1697 to corroboration."*
**Scientific authority delta:** `NONE`. No claim, ledger row, receipt or terminal was
changed by this record.

## 1. The exact theorem is not integrated, because it is not in the repository

**Terminal: `CANNOT_CHECK_ARTIFACT_ABSENT`.**

The board's ADOPT FIRST names a user handoff, `orion_top_tier_promotion_bundle(1).zip`.
It is not present, and the search that establishes this is stated so its scope can be
judged rather than trusted:

| search | scope | result |
|---|---|---|
| `find . -iname '*promotion_bundle*' -o -iname '*promotion-bundle*' -o -iname 'orion_top_tier*'` | whole worktree, dot-directories included | no match |
| `git log --all --diff-filter=A -- '*promotion_bundle*' '*promotion-bundle*'` | every ref in the repository, whole history | no match |
| `git grep -lniE 'orion_top_tier_promotion_bundle'` | `origin/main`, all paths | no match |
| `git grep -lE '156 dual\|dual-engine\|78 branches\|60 support'` | every ORION-04-related ref, `papers/orion-04*` | no match |

The no-alarm case is asserted rather than assumed: `git ls-files '*.zip'` returns ten
tracked archives, and `git log --all --diff-filter=A -- '*.zip'` returns many more across
history, so this repository does track `.zip` artifacts and a search of this shape is
capable of finding one. It did not find this one.

The theorem packet counts the board asks to verify — **60 support patterns, 78 branches,
156 dual-engine executions** — therefore have no artifact to verify against. They are
recorded as `CANNOT_CHECK_ARTIFACT_ABSENT`, not as unchecked and not as verified.

## 2. The manuscript is correct as it stands and was not edited

`MANUSCRIPT_V2.md` states `D_4(C_5^3) in {30,31}` (claim row N-C3, PROVEN INTERVAL) and
says in terms:

> `D_4(C_5^3)` remains 30/31; exact `D_4(C_5^3)` and `31 in C_0(C_5^3)` remain open. The
> paper is therefore a rigorous specialist manuscript with a sharper conceptual frontier,
> not yet a completed top-tier extremal theorem.

Editing this to assert `D_4(C_5^3)=30` on the strength of an absent bundle would be
fabrication. No manuscript byte was changed.

## 3. PR #1697 maps to corroboration, not to the exact theorem

The design/proof-producing lane is on `main` at
`evidence/crb-full-replay/successor-v1/engine_b/`. Its own scope statement in
`PROOF_OF_COMPLETENESS.md` is the mapping:

> the encoding is derived only from primitive `C_5^3` addition, with no orbit
> normalization, candidate filter, learned pruning rule, or imported NQ transition table

and, immediately after,

> It does not prove that an external input stream is a complete normalized census. That
> separate obligation is bound by an input-coverage declaration and still requires a
> proof auditor.

That is exactly corroboration-class authority: a second, independently derived decision
procedure that a shared encoding error could not produce, bounded away from the census
completeness obligation. It does **not** supply `D_4(C_5^3)=30`, and no row of
`CLAIM_LEDGER.md` is upgraded by it.

`SUBMISSION_BLOCKER.json` records the operative state: `status
AWAITING_NEW_ONE_SHOT_AUTHORIZATION`, `live_authorization: ABSENT`, `d2` and `d3`
`CANNOT_CHECK`, `d4` `OPEN` with `d4_rounds_consumed: 0`, `external_authority: false`,
`journal_authority: false`, `scientific_authority_delta: NONE`, and the operator
attestation explicitly `USER_SUPPLIED_UNVERIFIED_BY_MACHINE` with
`machine_established_externality: false`.

## 4. The CRB replay failure terminal is preserved

`NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__D2_D3_AUTHORITY_CANNOT_CHECK`
is present in nine committed locations, including
`evidence/crb-full-replay/post-execution/job-3544056/TERMINAL.txt`, its
`POST_EXECUTION_FAILURE_RECEIPT.json`, the successor's
`PRESERVED_FAILURE_BINDING_V1.json` and `DONOR_SOURCE_MANIFEST_V1.json`, and a test that
asserts on it. Nothing in this session touches any of them, and no `CANNOT_CHECK` is
converted anywhere.

## 5. Regression hazard: do not adopt `claude/orion04-crb-custody-adopt-20260828`

That branch's only ORION-04 change is to `CLAIM_LEDGER.md`, and it is a **weakening**.
`main` is ahead of it:

| row | `main` (keep) | that branch (reject) |
|---|---|---|
| N-C6 support bound | **at least 14**, authority *"M2/M3 parent plus Wave-3 M4 dual exact replay and independent receipt checker in `research/orion-rg/wave3/orion04-support11-13-v1/`"* | at least 11, authority *"M2/M3 symbolic reductions + isolated dual exact replay"* |
| headline decision proof | includes *"any upper-line length-31 obstruction must have support at least 14"* | that clause deleted |

Merging it would lower a proven bound from 14 to 11 and delete the Wave-3 evidence
citation. The branch was recovered path-by-path elsewhere in this session precisely so
this diff could be inspected rather than swept in; it is rejected with reason, not
silently skipped.

## 6. NEEDS_COMPUTE

Re-running the three independent handoff checkers is not possible: the handoff they
would run against is absent (§1). What *can* be re-run is the committed successor lane,
and it is gated on authorization rather than on compute — `SUBMISSION_BLOCKER.json`
§`required_before_submission` lists five preconditions including a **new operator-supplied
one-shot execution request** binding the exact successor commit, SOURCE_MANIFEST digest,
a fresh nonduplication key, a durable job root and a registry root outside the checkout,
run only via `slurm/submit_orion04_crb_full_replay.sh`, never reusing a historical key.
Both consumed keys are recorded in that file. No compute should be dispatched for this
lane until that authorization exists.
