# The premise-support transport law — ORION23.EXTERNAL_RESPONSIBILITY_TRANSPORT.v1

Top-tier promotion target from issue #1649, Tier A. `scientific_authority_delta: NONE`.

## What is already frozen

`P13_P14_OBJECTIVE_GOLD_RESULTS_V1.json` derives objective gold over **31 pinned
repositories in 14 organizations** — apache, emberjs, erlang, golang, jquery, microsoft,
pallets, pandas-dev, psf, pydata, redis, rust-lang, scipy, vuejs — with 123 facts decided
and **32 CANNOT_CHECK**, the latter because the locked per-repository runtime the contract
requires does not exist and *"an exit status obtained another way is not that fact"*.

#1649 asks for the theorem that formalises certificate transport on explicit load-bearing
premise support.

## Setting

A certificate `c` is issued against a finite set of **load-bearing premises**
`P(c) = {p_1, ..., p_k}`. On transport to a new state, each premise carries a status

    UNCHANGED | ENTAILED | CONTRADICTED | UNKNOWN

and the transport decision must be one of `REUSE`, `REVOKE`, `CANNOT_CHECK`.

Premises may themselves depend on premises, giving a support DAG `S`; write `A_S(Delta)`
for the affected closure of a change set as in `ORION16.REAL_SYSTEM_MINIMAL_REVALIDATION`.

## Theorem P1 (reuse is exactly the supported case)

`REUSE` is sound **iff** every `p in P(c)` has status `UNCHANGED` or `ENTAILED`.

*Proof.* (⇐) The certificate's derivation used only `P(c)`; if every premise still holds,
either unchanged or as an entailment of the new state, the derivation replays verbatim.
(⇒) If some `p` is `CONTRADICTED`, the derivation's hypothesis is false in the new state
and its conclusion is unsupported; if some `p` is `UNKNOWN`, no derivation is available
either way. ∎

## Theorem P2 (contradiction forces revocation, and it is not recoverable by re-checking)

If any load-bearing premise is `CONTRADICTED`, `REUSE` is unsound and no amount of
additional checking of the *other* premises restores it.

*Proof.* Soundness of reuse requires all of `P(c)`; a single false premise is a
counterexample regardless of the rest. ∎

## Theorem P3 (unknown is a third outcome, and collapsing it errs in a named direction)

If no premise is `CONTRADICTED` but some premise is `UNKNOWN`, the licensed output is
`CANNOT_CHECK` — neither `REUSE` nor `REVOKE`.

Collapsing `UNKNOWN` to either value is an error with a determinate direction:

- **UNKNOWN treated as UNCHANGED** yields unsound reuse — a certificate is carried on a
  premise nobody established.
- **UNKNOWN treated as CONTRADICTED** yields unnecessary revocation and recomputation —
  sound but wasteful.

*Proof.* Immediate from P1 and P2: the first case asserts support that is not established,
the second discards support that is not refuted. ∎

This is the load-bearing distinction of the paper. A two-valued transport rule **cannot**
express it, so it must either be unsound or over-conservative; there is no two-valued rule
that is both.

## Theorem P4 (minimal recomputation)

When transport fails, the set that must be recomputed is exactly `A_S(Delta)` over the
support DAG, and by `ORION16` N4 no nonnegative weighting of recomputation obligations
yields a cheaper sound set.

*Proof.* Certificates outside the affected closure have all premises unchanged and reuse by
P1; certificates inside may have a contradicted or unknown premise and are not licensed.
Minimality is `ORION16` N4 applied to `S`. ∎

## Corollary P5 (the three-valued ladder)

Ordering rules by how they treat `UNKNOWN` orders them by safety and cost in **opposite**
directions, exactly as graph inclusion did in `ORION16`: optimistic collapse is cheapest
and unsound, pessimistic collapse is safest and wasteful, and the three-valued rule is the
unique point that is both sound and minimal.

## Scope — prospective versus retrospective

**Prospective.** P1–P5 are proved here and verified by exhaustive enumeration over support
DAGs, all premise-status assignments, and all transport rules including both collapsing
rules, under a protocol frozen before that verification runs.

**Retrospective, licensing nothing.** `P13_P14_OBJECTIVE_GOLD_RESULTS_V1.json` records
`outcome_accessed: true`, so **no frozen test is run against it** and none is reported as
evidence.

**#1649's stop rule.** *If the external corpus does not support the broader transport
claim, retain the bounded current paper and publish the external boundary.* The corpus
records that every `TEST_EXIT` fact is `CANNOT_CHECK` because the locked runtime does not
exist. That is precisely `UNKNOWN` in the sense of P3 — an unestablished premise, not a
refuted one — so the corpus **exhibits** the boundary rather than crossing it. The stop
rule applies and the bounded paper is retained.

## What would refute this

A status assignment with all premises `UNCHANGED`/`ENTAILED` where reuse is unsound; a
`CONTRADICTED` premise where reuse is sound; an `UNKNOWN`-collapsing rule that is both
sound and never over-revokes; or a recomputation set smaller than the affected closure that
is still sound.
