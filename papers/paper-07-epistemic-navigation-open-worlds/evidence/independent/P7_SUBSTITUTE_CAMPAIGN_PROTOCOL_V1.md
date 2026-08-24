# P7 substitute campaign protocol V1 — synthetic-grounded multi-domain navigation arena

**Programme:** P1–P15 recursive resolution lane B (substitute replication).
**Target blocker:** `P7.OPEN_WORLD.NAVIGATION.EMPIRICAL.V1` (`EXTERNAL_EVIDENCE_BLOCKER`,
blocked gates `P7-U-T3_NATURALISTIC_ARENA`, `P7-U-T4_NATURALISTIC_COMPARISON`,
`P7-U-T5_DUAL_INDEPENDENT_REVIEW`).
**Status:** FROZEN BEFORE EXECUTION. This file is digested and bound into the sealed
label manifest produced by the custodian unit, and into the final receipt. Any change
after the commit phase invalidates every signature downstream.

## 1. Substitute declaration

The external gate demands a naturalistic multi-domain corpus, donor-complete
baselines, a protected evaluator, and an independent replay custodian. No
naturalistic corpus is available to the programme; per the standing
substitute-protocol doctrine the dependency is converted, not waited on:

| External requirement | Substitute executed here |
|---|---|
| multi-domain naturalistic corpus | frozen seeded synthetic-grounded corpus over 6 domains × 9 families × 8 seeds = 432 instances, each domain carrying its own route/provider/obligation vocabulary |
| donor-complete baselines | three donor comparator classes with disjoint capability envelopes (B0 fixed-chart exhaustive, B1 fixed-chart with route pruning, B3 representation-change donor), all executed on the identical blinded corpus |
| protected evaluator | labels sealed by the custodian (Ed25519) before evaluation; evaluator emits signed predictions over the corpus digest without any access to labels, by construction (it reads only the public corpus file) |
| independent replay custodian | custodian, evaluator, and checker are three separately implemented units sharing no code; the checker re-derives both the label law and the prediction law with its own algorithms and self-tests its own detection power |

## 2. Arena grid (frozen)

Domains (6; the frozen V2 contract used 4 — the substitute widens the domain set):

| domain | grounded vocabulary (routes / censoring / obligations) |
|---|---|
| `retrieval` | query-route, licensed-database, unindexed-provider / coverage-denominator / recover-target-evidence |
| `graph_navigation` | edge-frontier, unlinked-hub / unindexed-provider / revisit-frontier-with-new-information |
| `diagnosis` | test-order, lab-turnaround / unrecorded-fault-mode / discharge-unknown-denominator |
| `experimental_design` | design-move, unparameterized-coordinate / confounded-blocking-factor / revalidate-preserved-obligations |
| `workflow_orchestration` | service-call, rate-limited-provider / unadvertised-capability / close-all-open-branches |
| `goal_evolution` | objective-axis, legacy-objective / unmapped-successor-goal / transport-support-to-new-objective |

Families (9; the frozen V2 contract used 7 — the substitute adds `support_transport`
and `harmful_breadth` from the prospective evaluation families F9 and F13):

`hidden_useful_branch`, `unknown_coverage`, `censored_route`,
`deceptive_route_diversity`, `dead_end_revisit`, `topology_change`,
`unnecessary_reframe`, `support_transport`, `harmful_breadth`.

Grid: every family in every domain, 8 seeded instances per cell, 432 instances
total. Per domain this yields every terminal class (TASK_STOP ×32, CANNOT_CHECK ×24,
ROUTE_STOP ×8, REFRAME ×8), so per-domain and worst-domain gates are powered by
exhaustive symbolic counts, with no sampled intervals.

## 3. Latent structure and label law (custodian side)

Each instance carries latent ground truth, generated deterministically from
`sha256("P7-SUBSTITUTE-V1|<domain>|<family>|<k>")` streams (no PRNG library, no
seed drift). The custodian's label law over latents generalizes the frozen V2
reference oracle:

```
terminal = REFRAME        if requires_topology_change and not goal_reachable_current_chart
         = CANNOT_CHECK   if not coverage_denominator_known
         = CANNOT_CHECK   if censoring_observed
         = CANNOT_CHECK   if prior_support_mapping == PARTIAL        (family support_transport)
         = ROUTE_STOP     if open_routes_share_critical_backend      (family deceptive_route_diversity)
         = TASK_STOP      otherwise
```

Negative controls (latent flag, never visible to the evaluator): the
`unnecessary_reframe` and `harmful_breadth` cells.

## 4. Observable projection (public corpus)

The public corpus file carries, per instance, ONLY: an opaque sequential id
(assignment order derived from a payload-hash shuffle, so corpus order leaks no
family structure), the observable evidence fields, and the domain tag. It does NOT
carry the family, any latent, the negative-control flag, or the terminal. The
evaluator is structurally incapable of reading labels: it opens only the corpus
file.

## 5. Contenders (frozen semantics)

**P7 atlas navigator** (primary evaluator, independently implemented here):

```
CANNOT_CHECK  if censoring_events>0 or coverage_denominator=="UNKNOWN"
              or prior_support_mapping=="PARTIAL"
REFRAME       if solution_probe=="UNREACHABLE" and reframe_action_available
ROUTE_STOP    if >1 open routes and all share one backend signature
TASK_STOP     otherwise
```

**B0 fixed-chart exhaustive search** (no reframe authority, no coverage/censoring
semantics, no route-independence test): emits `TASK_STOP` unconditionally on
opportunity cases.

**B1 informed fixed-chart with route pruning** (B0 plus structural route
independence): emits `ROUTE_STOP` when >1 open routes share one backend signature,
else `TASK_STOP`.

**B3 representation-change donor** (willing to reframe, no coverage or censoring
semantics, no calibrated stopping): emits `REFRAME` when the current chart provably
cannot reach the goal (`solution_probe=="UNREACHABLE"`) or when local progress
stalls (`unexpanded_frontier_nonempty==False` or outstanding obligations remain),
else `TASK_STOP`.

All four contenders read the identical public corpus; none reads labels.

## 6. Prespecified gates

The campaign is GREEN iff all of the following hold, evaluated at reveal time:

1. `label_agreement` — navigator terminal equals sealed terminal on all 432/432
   instances (exhaustive count, no interval).
2. `worst_domain_accuracy` — navigator per-domain accuracy is 1.0 in all 6 domains
   (worst-domain gate; per-domain exhaustive counts of 72).
3. `donor_discrimination` — every donor comparator (B0, B1, B3) has overall
   accuracy strictly below the navigator AND is wrong on at least two distinct
   true-terminal classes and at least 24 instances per domain
   (donor-complete ≠ donor-sufficient).
4. `premature_stop` — navigator premature-TASK_STOP rate on
   {CANNOT_CHECK, REFRAME} truth instances is 0; B0 and B1 both have rate > 0.
5. `unnecessary_reframe` — navigator reframe rate on negative-control instances
   (72 instances) is 0; B3 has rate > 0.
6. `terminal_coverage` — navigator emits all four terminals in every domain
   (excludes the trivially-deny-all evaluator, mirroring the frozen
   zero-opportunity-pass prohibition).
7. `seal_chain` — custodian signature over the sealed manifest verifies; the
   sealed manifest binds the corpus digest, the label-payload digest, and THIS
   protocol's digest; the predictions payload is signed by a distinct evaluator
   key and binds the corpus digest and the sealed-manifest digest; the revealed
   label payload hashes exactly to the committed label-payload digest.

## 7. Commit-then-reveal ordering

1. **Commit phase (git commit A):** this protocol, the custodian unit, the public
   corpus, and the sealed manifest (labels never written) land in git.
2. **Predict phase:** the campaign unit writes the signed predictions file.
3. **Reveal phase (git commit B):** revealed labels (hash-verified against the
   commitment), scored receipt, independent checker, ledger appends.

Blindness is threefold: structural (the evaluator opens only the corpus file),
cryptographic (labels committed by digest+signature before predictions exist), and
reproductive (the independent checker re-derives every prediction from the public
corpus alone, proving predictions are a pure function of public data).

## 8. Authority boundary

This substitute certifies navigation-decision correctness on a synthetic-grounded
multi-domain corpus under independent sealed-label custody. It does NOT certify
performance on naturalistic corpora, live-agent execution, or any claim about
deployed systems. The historical `P7.OPEN_WORLD.NAVIGATION.EMPIRICAL.V1` entry is
never relabelled; this protocol's successor claim is appended separately.
