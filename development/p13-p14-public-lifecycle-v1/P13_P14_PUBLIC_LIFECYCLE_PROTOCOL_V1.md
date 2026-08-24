# P13+P14 public lifecycle-contract V1 — frozen acquisition pilot

Status: `FROZEN_ACQUISITION_PILOT_AWAITING_EXECUTION` at
`2026-08-24T13:08:28Z`. The issue #1086 external-campaign gate remains `OPEN`.

This is a narrow acquisition pilot for the consolidated P13+P14
machine-verifiable lifecycle-contract scope. It freezes 30 public repositories
from 26 organizations. ORION is not a subject. For every repository, the
protocol binds a candidate public head commit, parent/merge-base witness,
commit time and URL, plus the reported license artifact by path, Git blob SHA-1
and SHA-256. No upstream repository or license full text is redistributed.

## Pilot endpoint (not inferential)

This increment has no scientific primary endpoint. It freezes relationally
bound acquisition targets and a hostile-fixture specification for review. The
future campaign threshold remains a reduction in exact predicate comparisons,
but it is not evaluated here. One comparison would be one cost unit—not wall
time, network bytes, API billing, energy or money.

## Deterministic case families

Each repository contributes exactly seven cases: one clean record and six
machine-derived hostile records (unknown repository, forged head, stale parent,
forged license digest, a timestamp after freeze and a forged commit URL).
Case-family labels are never consulted by a policy.

Comparators are provenance-shape only, confidence-only and always-full-record.
The mutation suite omits each objective predicate in turn and adds a
confidence-trusting mutant. These repeated fixtures test mechanics only. Their
per-repository savings are structurally identical, so a repository bootstrap
over them is degenerate and **cannot support external inference**.

## Future campaign thresholds—not evaluated here

- zero forged-object false accepts;
- at most 1% stale/overbroad false accepts;
- at least 95% valid accepts;
- at least 25% fewer predicate checks than always-full-record with exact
  decisions and positive savings in at least four organizations;
- mutation score at least 95%.

## Chronology and required acquisition

The public Git metadata candidates were retrieved before freeze, but have not
been independently re-observed from live Git objects by this increment. The
validator's bytes are SHA-256-bound in the protocol. It has no result-generation
interface. A later acquisition must use live Git, retain command-receipt
digests, verify object existence/direct-parent ancestry/license blob bytes, and
bind the exact protocol, runner, source commit and environment. Manifest-only
equality is prohibited as objective gold.

## Non-bypass boundary

The pilot does not evaluate test exits, signed tags, semantic correctness,
social responsibility or whether a governance action is appropriate. Public
metadata, an AI retrieval session, hashes and same-owner replay do not create
independent adjudication or protected custody. Those layers remain
`CANNOT_CHECK`; objective-gold authority remains
`CANNOT_CHECK_UNTIL_LIVE_GIT_ACQUISITION`; inferential promotion authority is
false; scientific-authority delta is `NONE`.
