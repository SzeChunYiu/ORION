# The independent trust-domain law — ORION25.INDEPENDENT_TRUST_DOMAIN_LAW.v1

Top-tier promotion target from issue #1649, Tier A. Frozen before outcome access.
`scientific_authority_delta: NONE`.

## What is already frozen

`ORION25.EXECUTION_INTEGRITY.v1` established, on real receipts:

- **H1** — varying chain length at fixed trust domain leaves false promotion flat at
  `1.000`. Chain length buys nothing.
- **H2** — at `k = 3` with a single compromised domain, false promotion steps
  `1.00 -> 0.00 -> 0.00` as `d` goes `1 -> 2 -> 3`.
- false promotion `0` under applied artifact faults, false rejection `0/6` under
  semantics-preserving re-encoding, cross-site replay, and measured overhead.

H2 is one slice: `k` fixed at 3, exactly one domain compromised. #1649 asks for the
**law** — resilience controlled by trust-domain count as predicted, not by chain length.

## The model, exactly as frozen

`ROLES = (execution, environment, publication)`, so `k = 3` links, and a chain verifies
only if every role's link carries that role's expected public key. A **trust domain** is a
key-independence class: at `d = 1` every role key is derived from one shared deterministic
seed, so anyone who can run the runner derives them all; at `d > 1` each domain's key comes
from independent randomness, so no party can derive another domain's private key.

Let `alpha : ROLES -> Domains` assign each role to the domain holding its key, and let
`C` be the set of domains an adversary has compromised. Write

    supp(alpha) = alpha(ROLES),   d_eff = |supp(alpha)|

for the domains that actually hold at least one role.

## Theorem T (the law)

An adversary who compromises exactly the domains in `C` can forge an accepted chain **if
and only if** `supp(alpha) subset-of C`.

*Proof.* Verification requires, for every role, a link signed by that role's key.
(⇐) If `supp(alpha) ⊆ C` the adversary holds every role's private key and can re-sign the
whole chain on any claim, so it verifies. (⇒) If some role `r` has `alpha(r) not in C`,
its private key was generated from independent randomness inside an uncompromised domain
and is not derivable from `C`'s keys; the adversary cannot produce a link for `r` carrying
the expected public key and a valid signature, so verification fails at `r`. ∎

## Corollary T1 (the security parameter is `d_eff`, not `k`)

The minimum number of domains that must be compromised is exactly `d_eff`. It does not
depend on `k`, on chain length, or on which roles sit in which domain — only on how many
distinct domains hold roles.

This is the sharp form of what H1 and H2 each saw one slice of. H1 varied chain length at
`d_eff = 1` and correctly found no effect. H2 varied `d` with `|C| = 1` and found the step
exactly where `d_eff` first exceeded `|C|`.

## Corollary T2 (collapse)

Adding domains buys nothing unless roles are actually spread across them. If `alpha` maps
every role into one domain then `d_eff = 1` regardless of how many domains exist, and a
single compromise suffices. Domain *count* is not the parameter; domain *support* is.

## Corollary T3 (no false rejection)

`C = {}` gives `supp(alpha) ⊄ C` whenever `d_eff >= 1`, so an uncompromised chain is never
forged; and the honest chain always verifies because each role's link carries its own key.
Resistance is therefore purchased without any false-rejection cost, which is the
tradeoff #1649 asks to be measured rather than assumed.

## The limit this theory does NOT cross, stated before the experiment

`d > 1` is operationalised as **cryptographic** independence: keys generated from
independent randomness so one domain cannot derive another's secret. Every domain in this
programme is nevertheless held under **the same programme's custody**. Independent key
material is not organisational independence, and no experiment available here creates a
second custodian.

#1649's stop rule is explicit: *if independence cannot be operationalised beyond
same-programme custody, retain the bounded integrity paper and do not claim general
trust-domain resilience.* This packet therefore aims at the law under cryptographic
independence and, whatever it finds, does **not** claim general trust-domain resilience.
That is a scope limit fixed in advance, not a caveat added after seeing the numbers.

## What would refute this

Any `(alpha, C)` with `supp(alpha) ⊆ C` where the verifier rejects a forged chain, or any
`(alpha, C)` with `supp(alpha) ⊄ C` where it accepts one. Either direction kills Theorem T.
The experiment enumerates both directions exhaustively over the frozen role set and
requires a planted forgery to be detected, so that "no counterexample" is distinguishable
from "the search cannot see one".
