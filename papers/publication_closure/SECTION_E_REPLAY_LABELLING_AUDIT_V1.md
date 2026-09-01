# Section-E condition: replay labelling — audited and holding

**Audited:** 2026-09-01 against `origin/main`. **Authority delta:** `NONE`.
**Result:** the condition holds. Zero paper artifacts assert a completed external,
third-party, or outside-institution verification.

## The condition

Issue #1701 section E, *"Issue-level definition of done"*, requires that
**same-researcher clean-room replays are labelled precisely and never as external
investigators.** The hazard it guards is specific: a replay performed by the same
researcher, in a second implementation, reads to a referee as independent
corroboration if its label does not say otherwise. Overstating it once would
contaminate every claim resting on it.

## Scope, and why this scope

Every `.md` and `.json` file under `papers/` on `origin/main` — **3,837 files**, read
through `git show origin/main:<path>` rather than from the worktree, so the audit
describes what is published rather than what happens to be checked out locally.

One file could not be decoded as UTF-8:
`papers/orion-learning-machine/experiments/PHASE2_REAL_SOURCE_PLAN.md` (12,451 bytes).
It is **counted separately as could-not-check, never as clean**, and it sits in
`orion-learning-machine`, which is not one of the 25 numbered papers. Coverage across
the 25 is therefore complete.

## Method, and the false-positive class it had to survive

A first pass matched claim vocabulary — *external investigator / custodian /
replication / verification / audit*, *third-party replication / verification /
custody*, *independent investigator / laboratory / institution / group / team* — and
returned 171 occurrences, 119 of them without a nearby same-researcher qualifier.
**That result was not reportable**, and the reason matters: nearly all of those
sentences *require* external verification rather than claim it — "lacks a
self-contained external verification path", "External replication remains open", "no
role in this ledger counts as independent external verification". A checker that
matches the topic instead of the assertion cries wolf on its first real run.

The reported pass therefore demands three things of a single sentence: claim
vocabulary, a completed-assertion pattern (`was/were/has been … verified / replicated
/ audited / confirmed / performed / conducted / carried out / attested`), and the
absence of any requirement, negation, or modal marker. Both controls were exercised:
a positive probe, *"An external investigator was verified here"*, flags; the
requirement phrasing *"External replication remains open"* is suppressed.

## Result

**Zero flags across 3,837 files.**

The positive evidence sits alongside it. Fifty-two occurrences carry an explicit
same-researcher qualifier, so the programme is not silent on the distinction — it
states it. ORION-14's freeze addendum is the model: its clean-room replay is recorded
as a *second implementation inside the programme, not external custodianship*.

## What this does and does not settle

It settles one of the six substantive conditions in section E, on published content,
with a checker whose false-positive class was found and eliminated before any finding
was reported.

It does not bear on `independent_replay_attestation`, which is a different and
stricter object: that target requires a `ScientificResultVerification.v1` record with
`scorers.independent_from_written_spec: true`, and it remains correctly
`CANNOT_CHECK` for P6, P7 and P8. Passing this labelling audit is what honesty about
that gap looks like — the papers do not claim the independence they have not earned.
