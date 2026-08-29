# Claim disposition — ORION02.REFINEMENT_TO_CERTIFIABILITY.v1

Protocol and proof frozen at `b55ab5c82` before any outcome was read.
Terminal: **T1_REFINEMENT_CROSSES_THE_BOUNDARY_CONSTRUCTIVELY**.
Promotion status: **THEORY_STEP_COMPLETE__PROMOTION_NOT_YET_EARNED**.

## Result

| claim | violations |
|---|---|
| R1 midpoint certificate is `eps`-valid when `D <= 2 eps` | **0** |
| R2 `eps`-validity `<=>` `D <= 2 eps` | **0** |
| R3 greedy sweep count equals the exhaustive true minimum | **0** |
| R4 separator realisability characterisation | **0** |
| R5 coverage identity | **0** |

4,704 main configurations (fibre sizes 2–5 over a 7-value grid, six `eps` values) plus
the nested separator enumeration on sizes 2–4.

## What was promoted

`ORION02.FIBRE_DIAMETER_FLOOR.v1` established a barrier. This establishes that the
barrier is an **exact dial**:

- `eps`-validity on an accepted fibre holds **if and only if** `D(z) <= 2 eps` (R1+R2).
- The minimum number of parts needed to get there is **exactly** the greedy sweep count,
  verified against the true minimum over all set partitions (R3).
- Under a separator family `S`, that cost is attainable **iff** no `S`-indistinguishable
  pair differs by more than `2 eps` — otherwise the fibre is uncertifiable at any cost
  (R4). This recovers the original impossibility as the special case where `S` cannot see
  the difference at all.
- Coverage without refinement equals exactly the mass of fibres already within `2 eps`
  (R5).

That is #1649's requested relationship among fibre diameter, separator complexity,
achievable conditional risk, and the abstention/coverage tradeoff — as identities, not as
an empirical curve — and it is a constructive theorem crossing a previously proved
impossibility boundary.

## Controls, and two of mine that were vacuous

Every control plants a violation and requires the **same** predicate the real search uses
to catch it.

- **X1** — where the accepted certificate is not `eps`-valid, an index-seeing certificate
  must be, and the single shared `certifiable()` predicate must return False for the
  first and True for the second: **2792/2792**.
- **X2** — a deliberately wrong part-counter is run through the same `!=` comparison that
  decides R3, proving that comparison can fire: **2792/2792**. R3 is the claim most likely
  to be wrong, and it is checked against exhaustive true minima that share no code with
  the greedy routine.
- **X3** — silence on degenerate fibres: **0 alarms**.
- **X4** — planted unrealisable separator families detected: **8249/8249**.
- **X5** — at `eps = 0` the construction needs one part per distinct value, recovering the
  barrier rather than evading it: **784/784**.

X1 and X2 were **both vacuous in my first version** and were caught before anything was
reported. X1 tested `0.0 <= eps + TOL`, true by construction; X2 merely counted
comparisons without ever showing one could fail. Neither touched the machinery it claimed
to validate. This is the second time in this pass that a control of mine was a tautology,
which is the argument for the rule rather than against it: when the headline is an
absence, a control that cannot fire is worse than no control.

## What this does NOT license

**Promotion is not earned.** #1649 requires an empirical discriminator over at least four
disjoint real or externally sourced decision domains with information-matched baselines —
current fibre representation, lexical control, learned selector, strongest generic
representation learner, oracle refinement — showing theorem-guided refinement crossing the
predicted boundary with calibrated test-only risk control at useful coverage. That has
**not** been executed here, and `PROTOCOL.json` recorded its absence before outcomes were
read rather than after.

Nothing here bears on achievable risk on real data, revives any retracted ORION-02 claim,
or alters `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`.

Per #1649's hard prerequisite, no step uses the manuscript's unstated `A_t/B_t`
cross-gadget separability lemma; `A_t/B_t` is not cited here at all.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Outcomes were read once.
