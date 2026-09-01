# Provenance — ORION-04 global obstruction handoff

## What this is, and why it was missing

`HANDOFF_INTEGRATION_STATUS_V1.md` (2026-08-29) terminals at
`CANNOT_CHECK_ARTIFACT_ABSENT`, because the handoff it names —
`orion_top_tier_promotion_bundle(1).zip` — could not be found. That record's
searches were sound and are reproducible: the bundle is absent from the worktree
(dot-directories included) and from every ref across the whole history.

It was never committed. It sits in the operator's `~/Downloads`, under the name
`orion_top_tier_promotion_bundle.zip` — the recorded `(1)` is a browser
duplicate-download suffix, which is why a repository search for the literal name
found nothing.

- source file: `~/Downloads/orion_top_tier_promotion_bundle.zip`
- bundle SHA-256: `fcca596d9c7a2b42e50358386b6fa076bac6ed676a09a24b2cc959fe67ed17f0`
- extracted from: `research/orion-rg/top-tier/orion04-global-obstruction-v1/`

## What it establishes

`RESULT.json` terminal: **`ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30`**

> No length-31 total-zero sequence over `C_5^3` is free of nonempty zero sums of
> lengths at most five. Thus 31 is in `C_0(C_5^3)`; under the committed
> implication, `D_4(C_5^3) = 30`.

Internal checks recorded in the artifact: `branch_rows_78`, `cover_branches_78`,
`cover_patterns_60`, `all_exact_stdout_agreement`, `all_return_zero`,
`all_solutions_zero`, `all_stderr_empty` — 78 branches over 156 dual-engine runs
(`avx` and `u128` per family), matching the "156 dual-engine, 78 branches, 60
support" figures the board line cites.

## What it does NOT establish — carried from the artifact's own fields

- `novelty_authority: false`
- `external_independent_replay_complete: false`
- `submission_authority: false`

So this is a finite theorem with internal dual-engine agreement. It is **not**
externally replayed and its novelty is **not** assessed. Those are separate gates
and this commit claims neither.

## Relationship to the paper's current terminal

ORION-04 is frozen at `..._EXACT_D4_SUCCESSOR_ONLY`, and open PR #1674 proposes
closing it at `ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT`
with the bounded claim that a length-31 5-short-free obstruction, *if one exists*,
has support at least 14.

**This artifact addresses the same question and reports no such obstruction exists
at all.** That is a materially different terminal from the one #1674 proposes, so
the two must be reconciled by the paper's owner before either is filed. This commit
deliberately changes no ledger, terminal, manifest or `journal_package/` byte; it
only makes the previously absent input present and auditable.

An independent replay of all 156 engine runs is executing on a different host and
toolchain (gcc 13.2.0 vs the artifact's 14.2.0); its outcome will be reported
separately and will settle `external_independent_replay_complete` on evidence
rather than assertion.
