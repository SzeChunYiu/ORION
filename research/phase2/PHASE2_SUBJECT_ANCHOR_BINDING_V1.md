# Phase-2 subject-anchor binding V1

Read-only binding note for issue #76 against merged `main`. **This document
closes no gate, ticks no empirical checkbox, and grants no authority.** It
binds the Phase-1 terminal *anchor*. It does not name a Phase-2 closure
subject, because none exists.

Companion records (this lane, additive):

- `research/phase2/PHASE2_CLOSURE_GAP_LEDGER_V1.json` — checkbox-by-checkbox
  audit vs `origin/main`.
- `research/phase2/PHASE2_LIVE_PACKET_EXECUTION_CANNOT_CHECK_V1.json` — the
  live-packet execution verdict.

Machine-readable Phase-1 terminal receipt (sibling PR #271, **not on `main`
at authoring time**):

- `research/phase2/PHASE1_TERMINAL_SUBJECT_ANCHOR_V1.json`
- `provenance/phases/PHASE1_TERMINAL_RECEIPT_V1.json`

When #271 lands, those files are the canonical hashed form of the same
anchor identities recorded here. This note remains an as-of revalidation
against a later `main` head. On conflict, the hashed receipt governs.

## 1. Two objects that must not be conflated

| | Object | State on `main` at this audit |
|---|---|---|
| (a) | **Phase-1 terminal anchor** — the commit at which issue #75 declared `PHASE_1_CORE_TECHNICALLY_CLOSED` | Real, verifiable, bindable now |
| (b) | **Phase-2 closure subject** — the subject a closure run freezes via `freeze_phase2_binding()` | **Does not exist.** No closure run has occurred |

Issue #76's dependency line asks for evidence bound to "the exact final
Phase-1-derived subject used for the closure run". That subject is produced
*by* the run. Authoring a stand-in would be the `UNBOUND_EXECUTION_REPORT`
mislabel quarantined by #212. What is bindable now is (a) plus the
derivation predicate that a future (b) must satisfy.

## 2. Phase-1 terminal anchor (object a)

Verified 2026-08-17 from GitHub metadata plus this checkout's object store:

| Field | Value |
|---|---|
| commit_oid | `7983401847ea2b33706aacbf6e45b6bc63a60d0d` |
| tree_oid | `fd86b448b04e27ccd7ecc2372f1f391e6200c567` |
| merged pull request | #86 |
| issue | #75 (`CLOSED`) |
| declaring comment | [5307421385](https://github.com/SzeChunYiu/ORION/issues/75#issuecomment-5307421385) |
| terminal string | `PHASE_1_CORE_TECHNICALLY_CLOSED` |
| CI workflow | `ci` |
| CI run | `31946971360` |
| CI head_sha | `7983401847ea2b33706aacbf6e45b6bc63a60d0d` (equals the anchor) |
| CI conclusion | `success` |

`PHASE_1_CORE_TECHNICALLY_CLOSED` still does not appear in any tracked text
file on `main`. The terminal lives in the GitHub comment until PR #271's
receipt lands. This document records the identities; it does not invent a
repository-side receipt of a different schema.

## 3. Derivation predicate

A future `RepositorySubjectAttestation.v1` `S` is Phase-1-derived **iff**

```bash
git merge-base --is-ancestor 7983401847ea2b33706aacbf6e45b6bc63a60d0d <S.commit_oid>
```

exits 0. Exit 1 is not Phase-1-derived. Any other exit, or a missing object,
is `CANNOT_CHECK`, never `PASS`.

Ancestry is necessary and **not sufficient**. Issue #76 also requires every
evidence family to bind the same `subject_revision_hash` produced by the
closure run. Ancestry alone closes nothing.

The predicate must be re-evaluated at audit time. A history rewrite, a
force-update of `main`, or a subject taken from a branch that does not
contain the anchor all invalidate a previously true result.

## 4. As-of observation against current `main`

| Field | Value |
|---|---|
| observed_at | 2026-08-17 |
| audited_ref | `origin/main` |
| commit_oid | `266f6b94a285293364be7db86f4b98b526e7f4b8` |
| tree_oid | `7b9b1dae444bffeaa68f68c25e364ad666ef9e19` |
| `git cat-file -t` of the anchor | `commit` (object present in this checkout) |
| `git merge-base --is-ancestor <anchor> origin/main` | exit 0 |
| GitHub compare API `status` | `ahead` |
| GitHub compare API `behind_by` | 0 |
| GitHub compare API `ahead_by` | 406 |

Interpretation: as of this observation, `main` descends from the Phase-1
anchor with no recorded divergence, so a *future* closure subject taken from
`main` at or after `266f6b94` would satisfy the ancestry predicate. That is
an as-of fact, not a standing guarantee, and it is **not** a Phase-2
closure-subject binding.

## 5. Why Phase 2 is not closed

The frozen #8 live-trial packet
(`papers/orion-15-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json`,
fingerprint `53f99a2c7e6cfdd74cf5b10a62ba273bc911999b5719cf700eda64044f917e48`)
still has `corpus_revision: "UNBOUND"` at the packet top level and in both
task bindings. `outcome_accessed` is `false`. No merged live-execution
artifact is bound to a Phase-2 closure subject. The execution verdict is
therefore `CANNOT_CHECK` — see the companion JSON. `CANNOT_CHECK` is not
`FAIL` and is not `PASS`.

The terminal `PHASE_2_SHADOW_SELF_ORION_CLOSED` is **not issued**.

## 6. Explicit non-claims

- This document does not freeze a Phase-2 closure subject.
- This document does not execute, rewrite, or re-fingerprint the #8 packet.
- This document does not repair the fail-open preflight (#277 / PR #289) or
  the workflow/packet divergence (#8 / PR #275). Those files are owned by
  sibling lanes.
- This document does not grant Governed Self-ORION authority and does not
  move issue #209 or #210.
- `ahead_by` from the compare API is an as-of count, not a content hash.
  Do not treat it as a subject identity.
