# Claim disposition — ORION25.INDEPENDENT_TRUST_DOMAIN_LAW.v1

Protocol and theory frozen at `da94bf412` before any outcome was read.
Terminal: **T1_LAW_HOLDS_EXACTLY**.
Promotion status: **LAW_ESTABLISHED_UNDER_CRYPTOGRAPHIC_INDEPENDENCE__PROMOTION_NOT_EARNED**.

## Result

| | |
|---|---|
| cells swept | **1000** |
| cells matching Theorem T | **1000** |
| sufficiency failures (`supp(alpha) ⊆ C` but no forgery) | **0** |
| necessity failures (`supp(alpha) ⊄ C` yet forged) | **0** |

Every assignment of the three frozen roles to `d ∈ {1,2,3}` domains, crossed with every
subset `C` of compromised domains, on the real receipts.

## What the law says

Forgeability is exactly `supp(alpha) ⊆ C`. The security parameter is therefore
`d_eff = |supp(alpha)|` — the number of domains that actually hold a role — and it does
not depend on `k`, on chain length, or on which role sits where.

This subsumes both frozen slices rather than repeating them. `H1` varied chain length at
`d_eff = 1` and correctly found no effect; `H2` fixed `k = 3` and `|C| = 1` and found the
step exactly where `d_eff` first exceeded `|C|`. Both are one-dimensional cuts through the
same surface.

**Corollary T2 is the operationally important one**: domain *count* buys nothing unless
roles are actually spread. Five collapsing assignments (`d > 1` but `d_eff = 1`) appear in
the sweep, and in every one a single compromise forges. Provisioning three domains and
placing all roles in one is exactly as weak as having one.

**Corollary T3** holds too: honest chains verified in 1000/1000 cells, so resistance is
purchased at no false-rejection cost.

## Controls

- **C1** — where the theorem predicts forgery, forgery must actually succeed, or the
  attack is inert and every negative cell is meaningless: **260/260**.
- **C2** — the honest chain verified in **1000/1000** cells. A verifier that rejected
  honest chains would manufacture "resistance" for the wrong reason.
- **C3** — with nothing compromised, nothing forged: **144/144**.
- **C4** — collapsing assignments present: **5**. Without them T2 would be untested and
  the sweep vacuous for the corollary that matters most.

## The limit, fixed before the experiment

`d > 1` is **cryptographic** independence: keys from independent randomness, so no domain
can derive another's secret. Every domain nevertheless remains under **this programme's
custody**. Independent key material is not organisational independence, and no experiment
available here creates a second custodian.

#1649's stop rule is explicit: *if independence cannot be operationalised beyond
same-programme custody, retain the bounded integrity paper and do not claim general
trust-domain resilience.*

**That rule applies, and it applies on the favourable outcome.** The law is established
under cryptographic independence; general trust-domain resilience is **not** claimed;
ORION-25 stays in the bounded integrity lane. This scope limit was recorded in
`PROTOCOL.json` before outcomes were read, so it is not a caveat added once the numbers
came back clean.

## Authority

`MEASUREMENT_ONLY`. `scientific_authority_delta: NONE`. No submission authority. No new
attestation role was invented; the frozen three stand. Outcomes were read once.
